from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Shape, Mobility
from backend.python.functions import is_inside_polygon
from backend.python.transport.Transport import Transport
import numpy as np


class Location:
    DEBUG = False

    def __init__(self, ID: int, x: float, y: float,
                 shape: Shape,
                 exitx, exity, name: str):
        self.ID = ID
        self.x = x
        self.y = y
        self.shape = shape
        self.boundary = []  # list of polygon points of the boundary [(x1,y1),(x2,y2), ...]
        self.radius = 0  # radius if shape is circle
        self.exit = (exitx, exity)

        self.infectious = 1.0

        self.points = []
        self.points_enter_time = []

        self.parent_location = None
        self.locations = []
        self.depth = 0

        self.transport_mediums = []
        self.override_transport: Transport = None
        self.name = name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

    def get_suggested_waiting_duration(self, point):
        raise NotImplementedError()

    def add_sub_location(self, location):
        location.parent_location = self
        location.depth = self.depth + 1
        self.locations.append(location)

        def f(ll):
            for ch in ll.locations:
                ch.depth = ll.depth + 1
                f(ch)

        f(location)

    def set_boundary(self, boundary):
        boundary = np.array(boundary)
        self.boundary = boundary
        self.x = np.mean(boundary[:, 0])
        self.y = np.mean(boundary[:, 1])
        self.exit = (self.x, self.y)

    def set_radius(self, r):
        self.radius = r

    def process_inter_location_transport(self, t):
        # processing transportation handled by this location
        for point in self.points:
            point.current_trans.move(point, t)

    def process_people_movement(self, t):
        # DFS each location graph and process leaf locations
        for i, point in enumerate(self.points):
            # check if the time spent in the current location is above
            # the point's staying threshold for that location

            if t - self.points_enter_time[i] > point.duration_time[point.current_location]:
                # overstay. move point to the transport medium
                next_location = MovementEngine.find_next_location(point)

                if self.depth == next_location.depth:
                    transporting_location = self.parent_location
                elif self.depth > next_location.depth:
                    transporting_location = next_location
                else:
                    transporting_location = self
                transporting_location.enter_person(point, t, next_location)

            # else:
            #     # doing stuff in the current location
            #     point.current_trans.move_point(self, point)
        if len(self.locations) == 0:
            if self.override_transport is None:
                raise Exception("Leaf locations should always override transport")


        else:
            for location in self.locations:
                location.process_people_movement(t)

        self.process_inter_location_transport(t)

    def add_to_inter_location_transport(self, transporting_location, target_location, idx, t):

        transporting_location.enter_person(self.points[idx], t, target_location)

    def enter_person(self, p, t, target_location=None):
        if p.current_loc is not None:
            p.current_loc.remove_point(p)
        self.points.append(p)
        self.points_enter_time.append(t)

        if self.override_transport is not None:
            trans = self.override_transport
        else:
            trans = p.main_trans
        trans.add_point_to_transport(p, target_location, t)
        if Location.DEBUG:
            print(f"### Enter {p} to {target_location} through {self} using {trans}")
        p.current_loc = self

    def remove_point(self, point):
        idx = self.points.index(point)
        self._remove_point(idx)

    def _remove_point(self, idx):
        self.points.pop(idx)
        self.points_enter_time.pop(idx)

    def is_inside(self, x, y):
        if self.shape == Shape.POLYGON.value:
            return is_inside_polygon(self.boundary, (x, y))
        if self.shape == Shape.CIRCLE.value:
            return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.radius ** 2
