from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.const import DAY
from backend.python.enums import Shape
from backend.python.functions import is_inside_polygon
from backend.python.Time import Time
import numpy as np


class Location:
    DEBUG = False
    _id = 0

    def __init__(self, shape, x, y, name, exittheta=0.0, exitdist=0.9, infectiousness=1.0, **kwargs):
        self.ID = Location._id
        Location._id += 1
        self.x = x
        self.y = y
        self.shape = shape
        self.depth = 0
        self.capacity = kwargs.get('capacity')
        self.recovery_p = 0.1  # todo find this, add to repr

        self.quarantined = kwargs.get('quarantined', False)
        self.quarantined_time = -1

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
        self.is_visiting = []

        self.parent_location = None
        self.locations = []
        self.override_transport = None
        self.name = name

    def __repr__(self):
        d = self.get_description_dict()
        return ','.join(map(str, d.values()))

    def __str__(self):
        return self.name

    def get_description_dict(self):
        d = {'class': self.__class__.__name__, 'id': self.ID, 'x': self.x, 'y': self.y, 'shape': self.shape,
             'depth': self.depth, 'capacity': self.capacity, 'quarantined': self.quarantined,
             'quarantined_time': self.quarantined_time, 'exit': self.exit.__str__().replace(',', '|').replace(' ', ''),
             'infectious': self.infectious, "name": self.name}

        if self.shape == Shape.CIRCLE.value:
            d['radius'] = self.radius
        elif self.shape == Shape.POLYGON.value:
            d['boundary'] = self.boundary.__str__().replace(',', '|').replace(' ', '')

        if self.parent_location is None:
            d['parent_id'] = -1
        else:
            d['parent_id'] = self.parent_location.ID

        if self.override_transport is None:
            d["override_transport"] = -1
        else:
            d["override_transport"] = self.override_transport.ID
        return d

    def spawn_sub_locations(self, cls, n, r, infectiousness, trans, **kwargs):
        xs, ys = self.get_suggested_positions(n, r)
        print(f"Automatically creating {len(xs)}/{n} {cls.__name__} for {self.__class__.__name__} {self.name}")
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
                for _theta in range(int(np.pi * 1000) // int(theta * 1000)):
                    _theta = theta * 2 * _theta
                    _x = _r * np.cos(_theta)
                    _y = _r * np.sin(_theta)
                    # check if the current circle intersect another location
                    if not self.is_intersecting(_x + x, _y + y, r2):
                        all.append((_x + x, _y + y))

            if _r > r2 and not self.is_intersecting(x, y, r2):
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

    def set_quarantined(self, quarantined, t, recursive=False):
        self.quarantined = quarantined
        if recursive:
            def f(r: Location):
                r.quarantined = quarantined
                if quarantined:
                    r.quarantined_time = t
                else:
                    r.quarantined_time = -1
                for ch in r.locations:
                    f(ch)

            f(self)

    def add_sub_location(self, location):
        location.parent_location = self
        location.depth = self.depth + 1
        self.locations.append(location)

        def f(ll):
            for ch in ll.locations:
                ch.depth = ll.depth + 1
                f(ch)

        f(location)

    def check_for_leaving(self, t):
        for i, p in enumerate(self.points):
            # check if the time spent in the current location is above
            # the point's staying threshold for that location
            if t - p.current_loc_leave > Time.get_duration(5):
                Logger.log(
                    f"OT while check for leaving {p} Not leaving current place {p.get_current_location().name} "
                    f"after timeout! dt={t - p.current_loc_leave} "
                    f"Day over? {p.is_day_finished} "
                    f"In home? {p.get_current_location() == p.route[0]} "
                    f"Going to another? {p.in_inter_trans} "
                    f"Logic ({p.is_day_finished} and {p.get_current_location() == p.route[0]}) or {p.in_inter_trans} "
                    f"Move  {p.current_trans}"
                    , 'w'
                )

            # come to route[0] if not there even if day is finished
            if t >= p.current_loc_leave:
                if p.is_day_finished and p.get_current_location() == p.route[0]:
                    continue
                if p.in_inter_trans:
                    continue
                # overstay. move point to the transport medium
                next_location = MovementEngine.find_next_location(p)

                if self.depth == next_location.depth:
                    transporting_location = self.parent_location
                elif self.depth > next_location.depth:
                    transporting_location = next_location
                else:
                    transporting_location = self

                if transporting_location is None:
                    transporting_location = self  # this is because when we update route we set current_loc to root sometimes
                assert next_location is not None
                # leaving current location
                if ContainmentEngine.can_go_there(p, self, next_location):
                    transporting_location.enter_person(p, next_location)
                    p.in_inter_trans = True

    def enter_person(self, p, target_location=None):
        t = Time.get_time()
        current_loc_leave = self.get_leaving_time(p, t)
        is_visiting = True
        if p.get_current_location() is None:  # initialize
            pass
        else:
            p.get_current_location().remove_point(p)
            if p.get_next_target() == self:
                is_visiting = False
                p.increment_target_location()
                current_loc_leave = self.get_leaving_time(p, t)
            elif p.get_current_target() == self:
                pass
            else:
                current_loc_leave = t - 1

        p.current_loc_enter = t
        p.current_loc_leave = current_loc_leave
        self.points.append(p)
        self.is_visiting.append(is_visiting)
        p.set_current_location(self, t)

        # following lines should be always after the above code
        p.on_enter_location(t)

        if self.capacity is not None:
            if self.capacity < len(self.is_visiting)-sum(self.is_visiting):
                # CURRENT LOCATION FULL.
                if is_visiting:
                    # if the added person is only visiting the current location. nothing to worry
                    pass
                else:
                    # added person wanted to visit the current location but it's full. IMMEDIATELY REMOVE.

                    # Move to next location to each next target.
                    # move to parent location because we can't add to current location and we can move down the tree

                    Logger.log(f"CAPACITY reached on {self} when entering person {p.ID}! "
                               f"All:{len(self.is_visiting)} "
                               f"Visiting:{sum(self.is_visiting)} "
                               f"Staying:{len(self.is_visiting)-sum(self.is_visiting)} "
                               f"Capacity:{self.capacity}")
                    if self.parent_location is not None:
                        next_location = MovementEngine.find_next_location(p)
                        Logger.log(f"Person {p.ID} will be removed from current location {self} "
                                   f"and it will be added to parent location {self.parent_location}"
                                   f"to reach {next_location}.", 'c')
                        self.parent_location.enter_person(p, next_location)

                        # todo bug: if p is in home, when cap is full current_loc jump to self.parent
                        return  # don't add to this location because capacity reached
                    raise Exception("Capacity full at root node!!! Cannot handle this!")
        if not p.latched_to:
            # add the person to the default transportation system, if the person is not latched to someone else.
            if self.override_transport is not None:
                trans = self.override_transport
            else:
                trans = p.main_trans
            trans.add_point_to_transport(p, target_location)
            Logger.log(f"Entered {p.ID} to {self.name} using {trans}. Destination {target_location}", 'e')
        else:
            Logger.log(f"Entered {p.ID} to {self.name} latched with {p.latched_to.ID} Destination {target_location}", 'e')

    def get_leaving_time(self, p, t):
        if p.duration_time[p.current_target_idx] != -1:
            current_loc_leave = min(t + p.duration_time[p.current_target_idx], t - t % DAY + DAY - 1)
        else:
            # bias = (t // DAY) * DAY
            # if p.is_day_finished:
            #     bias += DAY
            current_loc_leave = p.leaving_time[p.current_target_idx]%DAY + t - t % DAY
        if p.is_day_finished and self == p.home_loc:
            if current_loc_leave < t - t % DAY + DAY:
                current_loc_leave += DAY
        return current_loc_leave

    def remove_point(self, point):
        idx = self.points.index(point)
        self._remove_point(idx)

    def _remove_point(self, idx):
        self.points.pop(idx)
        self.is_visiting.pop(idx)

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
