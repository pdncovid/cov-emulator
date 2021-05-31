from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Shape
from backend.python.functions import is_inside_polygon, get_time, get_duration
import numpy as np


class Location:
    DEBUG = False
    _id = 0
    _day = get_duration(24)

    def __init__(self, shape, x, y, name, exittheta=0.0, exitdist=0.9, infectiousness=1.0, **kwargs):
        self.ID = Location._id
        Location._id += 1
        self.x = x
        self.y = y
        self.shape = shape
        self.capacity = kwargs.get('capacity')
        self.boundary = []  # list of polygon points of the boundary [(x1,y1),(x2,y2), ...]
        self.radius = 0  # radius if shape is circle
        if shape == Shape.CIRCLE.value:
            self.radius = kwargs.get('r')
            if self.radius is None:
                raise Exception("Please provide radius")
            self.exit = (x + np.cos(exittheta) * self.radius * exitdist, y + np.sin(exittheta) * self.radius * exitdist)
        elif shape == Shape.POLYGON.value:
            self.boundary = kwargs.get('b')
            if self.boundary is None:
                raise Exception("Please provide boundary")
            # TODO add exit point here
            self.x = np.average(self.boundary[:, 0])
            self.y = np.average(self.boundary[:, 1])
            self.exit = (self.x * (1 - exitdist) + self.boundary[0, 0] * exitdist,
                         self.y * (1 - exitdist) + self.boundary[0, 1] * exitdist)

        self.infectious = infectiousness

        self.points = []

        self.parent_location = None
        self.locations = []
        self.depth = 0

        self.transport_mediums = []
        self.override_transport = None
        self.name = name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

    def spawn_sub_locations(self, cls, n, r, infectiousness, trans, **kwargs):
        print(f"Automatically creating {n} {cls.__name__} for {self.__class__.__name__} {self.name}")
        xs, ys = self.get_suggested_positions(n, r)
        i = 0
        for x, y in zip(xs, ys):
            building = cls(Shape.CIRCLE.value, x, y, self.name + '-' + cls.__name__[:3] + str(i),
                           infectiousness=infectiousness, r=r, **kwargs)
            building.override_transport = trans
            self.add_sub_location(building)
            i += 1

    def get_suggested_positions(self, n, radius):

        if self.shape == Shape.CIRCLE.value:
            all = []
            x = self.x
            y = self.y
            r1 = self.radius
            r2 = radius
            _r = 0
            for _r in range(int((r1 - r2) // (2 * r2))):
                _r = r1 - r2 - 2 * r2 * _r

                theta = np.arcsin(r2 / _r)
                print(_r, theta, np.pi // theta, np.pi % theta)
                for _theta in range(int(np.pi * 1000) // int(theta * 1000)):
                    _theta = theta * 2 * _theta
                    _x = _r * np.cos(_theta)
                    _y = _r * np.sin(_theta)
                    # check if the current circle intersect another location
                    if not self.is_intersecting(_x + x, _y + y, r2):
                        all.append((_x + x, _y + y))

            if _r > r2:
                all.append((x, y))

            # pick the n (x, y) points

            idx = np.arange(len(all))
            np.random.shuffle(idx)
            if len(idx) < n:
                print(f"Cannot make {n} locations with {radius}. Making only {len(idx)} locations")
            else:
                idx = idx[:n]
            x = [all[c][0] for c in idx]
            y = [all[c][1] for c in idx]

        elif self.shape == Shape.POLYGON.value:
            # TODO
            raise NotImplementedError()
        else:
            raise NotImplementedError()

        return x, y

    def get_leaves_of_class(self, cls):
        leaves = []

        def dfs(rr: Location):
            if len(rr.locations) == 0:
                if isinstance(rr, cls):
                    leaves.append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(self)
        return leaves

    def get_children_of_class(self, cls):
        return [b for b in self.locations if isinstance(b, cls)]

    def get_suggested_sub_route(self, point, t, force_dt=False) -> (list, list, list, int):
        raise NotImplementedError()

    @staticmethod
    def separate_into_classes(root):
        classes = {}

        def dfs(rr: Location):
            if rr.__class__ not in classes.keys():
                classes[rr.__class__] = []
            classes[rr.__class__].append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(root)

        return classes

    def add_sub_location(self, location):
        location.parent_location = self
        location.depth = self.depth + 1
        self.locations.append(location)

        def f(ll):
            for ch in ll.locations:
                ch.depth = ll.depth + 1
                f(ch)

        f(location)

    def process_inter_location_transport(self, t):
        # processing transportation handled by this location
        for point in self.points:
            point.current_trans.move(point, t)

    def process_people_movement(self, t):
        # DFS each location graph and process leaf locations
        for i, point in enumerate(self.points):
            # check if the time spent in the current location is above
            # the point's staying threshold for that location

            if t >= point.current_loc_leave and point._reset_day == False and point.in_inter_trans == False:  # TODO and _reset is bugsy
                # overstay. move point to the transport medium
                next_location = MovementEngine.find_next_location(point)

                if self.depth == next_location.depth:
                    transporting_location = self.parent_location
                elif self.depth > next_location.depth:
                    transporting_location = next_location
                else:
                    transporting_location = self
                if transporting_location is None:
                    transporting_location = self  # this is because when we update route we set current_loc to root sometimes

                # leaving current location
                transporting_location.enter_person(point, t, next_location)
                point.in_inter_trans = True

        if len(self.locations) == 0:
            if self.override_transport is None:
                raise Exception("Leaf locations should always override transport")
        else:
            for location in self.locations:
                location.process_people_movement(t)

        self.process_inter_location_transport(t)

    def enter_person(self, p, t, target_location=None):

        current_loc_leave = self.get_leaving_time(p, t)
        if p.current_loc is None:  # initialize
            pass
        else:
            p.current_loc.remove_point(p)
            if p.get_next_location() == self:
                p.current_location = (p.current_location + 1) % len(p.route)
                current_loc_leave = self.get_leaving_time(p, t)
            else:
                current_loc_leave = t - 1
        if self.capacity is not None:
            if self.capacity <= len(self.points):
                p.current_location = (p.current_location + 1) % len(p.route)
                current_loc_leave = t - 1

        p.current_loc = self
        p.current_loc_enter = t
        p.current_loc_leave = current_loc_leave
        self.points.append(p)
        if self.override_transport is not None:
            trans = self.override_transport
        else:
            trans = p.main_trans
        trans.add_point_to_transport(p, target_location, t)

        if Location.DEBUG:
            print(f"### Enter {p} to {target_location} through {self} using {trans}")

    def get_leaving_time(self, p, t):
        if p.duration_time[p.current_location] != -1: # p.current
            current_loc_leave = min(t + p.duration_time[p.current_location], Location._day - 1)
        else:
            current_loc_leave = (p.leaving_time[p.current_location])
        return current_loc_leave

    def remove_point(self, point):
        idx = self.points.index(point)
        self._remove_point(idx)

    def _remove_point(self, idx):
        self.points.pop(idx)

    def is_inside(self, x, y):
        if self.shape == Shape.POLYGON.value:
            return is_inside_polygon(self.boundary, (x, y))
        if self.shape == Shape.CIRCLE.value:
            return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.radius ** 2

    def is_intersecting(self, x, y, r):
        _is = False
        for l in self.locations:
            if l.shape == Shape.CIRCLE.value:
                if (l.x - x) ** 2 + (l.y - y) ** 2 < r ** 2 + l.radius ** 2:
                    _is = True
                    break
            # todo other shapes
        return _is
