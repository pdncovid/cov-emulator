from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Shape, Mobility
from backend.python.functions import is_inside_polygon
from backend.python.transport.Transport import Transport
import numpy as np

class Location:
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
        self.points_in_transport = []
        self.points_in_transport_enter_time = []
        self.points_in_transport_destination = []

        self.parent_location = None
        self.locations = []
        self.depth = 0

        self.transport_mediums = []
        self.override_transport: Transport = None
        self.name = name

    def get_suggested_waiting_duration(self,point):
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
        self.boundary = boundary
        self.x = np.mean(boundary[:][0])
        self.y = np.mean(boundary[:][1])

    def set_radius(self, r):
        self.radius = r

    def process_point_movement(self, t):
        # DFS each location graph and process leaf locations
        if len(self.locations) == 0:
            for i, point in enumerate(self.points):
                # check if the time spent in the current location is above
                # the point's staying threshold for that location

                if t - self.points_enter_time[i] > point.duration_time[point.current_location]:
                    # overstay. move point to the transport medium
                    next_location = MovementEngine.find_next_location(point)

                    if self.depth == next_location.depth:
                        self.add_to_transport(self.parent_location, next_location, i, t)
                    elif self.depth > next_location.depth:
                        self.add_to_transport(next_location, next_location, i, t)
                    else:
                        self.add_to_transport(self, next_location, i, t)
                else:
                    # doing stuff in the current location
                    if self.override_transport is None:
                        raise Exception("Leaf locations should always override transport")
                    self.override_transport.move_point(self, point)

        else:
            for location in self.locations:
                location.process_point_movement(t)

        # processing transportation handled by this location
        i = 0
        while i < len(self.points_in_transport):

            point = self.points_in_transport[i]
            if self.override_transport is None:
                trans = point.main_trans
            else:
                trans = self.override_transport
            destination: Location = self.points_in_transport_destination[i]
            trans.transport_point(point, destination.exit)

            if MovementEngine.is_close(point, destination.exit[0], destination.exit[1], eps=10.0):

                if point.get_next_location() == destination:
                    destination.add_point(point, t)
                    point.current_location = (point.current_location + 1) % len(point.route)
                else:
                    # even though we add it to the point it should immediately go at next iteration
                    destination.add_point(point, -10000000000)
                self.points_in_transport.pop(i)
                self.points_in_transport_enter_time.pop(i)
                self.points_in_transport_destination.pop(i)
                i -= 1
            i += 1

    def add_to_transport(self, transporting_location, target_location, idx, t):
        transporting_location.points_in_transport.append(self.points[idx])
        transporting_location.points_in_transport_enter_time.append(t)
        transporting_location.points_in_transport_destination.append(target_location)

        self._remove_point(idx)

    def add_point(self, p, t):
        self.points.append(p)
        self.points_enter_time.append(t)

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
