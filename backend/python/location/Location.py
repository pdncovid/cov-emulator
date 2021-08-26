from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target

from backend.python.enums import Shape
from backend.python.functions import get_random_element
from backend.python.Time import Time
import numpy as np

from backend.python.point.Transporter import Transporter


class Location:
    DEBUG = False
    all_locations = []
    _id = 0

    def __init__(self, shape, x, y, name, **kwargs):
        from backend.python.const import default_infectiousness
        self.ID = Location._id
        Location._id += 1
        self.x = x
        self.y = y
        self.shape = shape
        self.depth = 0
        self.capacity = kwargs.get('capacity')
        self.recovery_p = 0.1  # todo find this, add to repr

        self.infectious = default_infectiousness[self.__class__] if kwargs.get(
            'infectiousness') is None else kwargs.get('infectiousness')

        self.quarantined = kwargs.get('quarantined', False)
        self.quarantined_time = -1

        self.boundary = []  # list of polygon points of the boundary [(x1,y1),(x2,y2), ...]
        self.radius = 0  # radius if shape is circle

        exitdist = kwargs.get('exitdist', 0.9)
        if shape == Shape.CIRCLE.value:
            exittheta = kwargs.get('exittheta', 0.0)
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

        self.points = []
        self.is_visiting = []

        self.parent_location = None
        self.locations = []
        self.override_transport = None
        self.name = name
        Location.all_locations.append(self)

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

    def spawn_sub_locations(self, cls, n_sub_loc, r_sub_loc, **kwargs):
        if n_sub_loc <= 0:
            return
        assert r_sub_loc > 0
        xs, ys = self.get_suggested_positions(n_sub_loc, r_sub_loc)
        print(f"Automatically creating {len(xs)}/{n_sub_loc} {cls.__name__} for {self.__class__.__name__} {self.name}")
        kwargs['r'] = r_sub_loc
        i = 0
        for x, y in zip(xs, ys):
            building = cls(Shape.CIRCLE.value, x, y, self.name + '-' + cls.__name__[:3] + str(i), **kwargs)
            self.add_sub_location(building)
            i += 1

    def get_suggested_positions(self, n, radius):

        if self.shape == Shape.CIRCLE.value:
            possible_positions = []
            failed_positions = []
            x = self.x
            y = self.y
            r1 = self.radius
            r2 = radius
            _r = 0
            for _r in range(int((r1) // (2 * r2))):
                _r = r1 - r2 - 2 * r2 * _r

                theta = np.arcsin(r2 / _r)
                for _theta in range(int(np.pi * 1000) // int(theta * 1000)):
                    _theta = theta * 2 * _theta
                    _x = _r * np.cos(_theta)
                    _y = _r * np.sin(_theta)
                    # check if the current circle intersect another location
                    if not self.is_intersecting(_x + x, _y + y, r2, eps=r2 // 2):
                        possible_positions.append((_x + x, _y + y))
                    else:
                        failed_positions.append((_x + x, _y + y))
            if _r > r2 and not self.is_intersecting(x, y, r2, eps=r2 // 2):
                possible_positions.append((x, y))

            # pick the n (x, y) points

            if len(possible_positions) < n:
                print(f"Cannot make {n} locations with {radius}. Making only {len(possible_positions)} locations")
                while len(possible_positions) != n:
                    possible_positions.append(failed_positions.pop())
            else:
                possible_positions = possible_positions[:n]
            idx = np.arange(len(possible_positions))
            np.random.shuffle(idx)
            x = [possible_positions[c][0] for c in idx]
            y = [possible_positions[c][1] for c in idx]

        elif self.shape == Shape.POLYGON.value:
            # TODO
            raise NotImplementedError()
        else:
            raise NotImplementedError()

        return x, y

    def get_locations_according_function(self, f):
        leaves = []

        def dfs(rr: Location):
            if f(rr):
                leaves.append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(self)
        return leaves

    def get_children_of_class(self, cls):
        return [b for b in self.locations if isinstance(b, cls)]

    def get_root(self):
        rr = self
        while rr.parent_location is not None:
            rr = rr.parent_location
        return rr

    def get_suggested_sub_route(self, point, route_so_far) -> list:
        t = route_so_far[-1].leaving_time if len(route_so_far) > 0 else Time.get_time()
        dur = RoutePlanningEngine.get_dur_for_p_in_loc_at_t(point, self, t)
        _r = [Target(self, t + dur, None)]
        route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        return route_so_far

    def get_distance_to(self, loc):
        return ((self.x - loc.x) ** 2 + (self.y - loc.y) ** 2) ** 0.5

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

            # come to route[0] if not there, even if day is finished
            if t >= p.current_loc_leave:
                if p.latched_to is not None:
                    continue
                if p.is_day_finished and p.get_current_location() == p.route[0].loc:
                    continue
                if p.all_destinations[p.ID] != -1:
                    # waiting too long in this place!!!
                    if t - p.current_loc_leave > Time.get_duration(1) and \
                            t - p.current_loc_enter > Time.get_duration(1):
                        Logger.log(
                            f"OT {p} @ {p.get_current_location().name} -> {MovementEngine.find_next_location(p)} [{p.get_next_target()}] "
                            f"({p.current_target_idx}/{len(p.route)}) "
                            f"dt={t - p.current_loc_leave} "
                            f"Move {p.current_trans} "
                            f"ADD TO Walk"
                            , 'c'
                        )
                        from backend.python.transport.Walk import Walk
                        walk = get_random_element(Walk.all_instances)
                        walk.add_point_to_transport(p)
                    elif t - p.current_loc_leave > Time.get_duration(0.5) and \
                            t - p.current_loc_enter > Time.get_duration(0.5):
                        # todo change current transportation system to tuk tuk or taxi
                        Logger.log(
                            f"OT {p} @ {p.get_current_location().name} -> ({p.get_next_target()}) "
                            f"({p.current_target_idx}/{len(p.route)}) "
                            f"dt={t - p.current_loc_leave} "
                            f"Move {p.current_trans} "
                            f"ADD TO Tuktuk"
                            , 'c'
                        )
                        from backend.python.transport.Tuktuk import Tuktuk
                        tuktuk = get_random_element(Tuktuk.all_instances)
                        tuktuk.add_point_to_transport(p)
                    continue

                self.leave_this_location(p)

    def leave_this_location(self, p):
        # overstay. move point to the transport medium
        next_location = MovementEngine.find_next_location(p)

        if self.depth == next_location.depth:
            transporting_location = self.parent_location
        elif self.depth > next_location.depth:
            transporting_location = next_location
        else:
            transporting_location = self

        if transporting_location is None:
            # this is because when we update route we set current_loc to root sometimes
            transporting_location = self

        assert next_location is not None

        # leaving current location
        can_go_out_movement = transporting_location.can_enter(p)
        can_go_out_containment = ContainmentEngine.can_go_there(p, self, next_location)
        if can_go_out_containment and can_go_out_movement:
            p.set_point_destination(next_location)
            Logger.log(f"{p.ID} move {p.get_current_location()} -> {next_location} ({transporting_location}) [{p.get_next_target()}]", 'd')
            transporting_location.enter_person(p)
            # p.in_inter_trans = True
        else:
            if not can_go_out_movement:
                transporting_location.set_movement_method(p)
            Logger.log(f"{p.ID} cannot leave {self}", 'd')

    def can_enter(self, p):
        from backend.python.transport.MovementByTransporter import MovementByTransporter
        if isinstance(p, Transporter):
            return True
        if p.latched_to is not None:
            return True
        if self.override_transport is None and isinstance(p.main_trans, MovementByTransporter):
            return False
        return True

    def on_destination_reached(self, p):
        Logger.log(f"Destination {self} reached by {p}", 'd')
        p.set_point_destination(None)
        self.enter_person(p)

    def enter_person(self, p):
        if p.get_current_location() is not None:
            p.get_current_location().remove_point(p)

        t = Time.get_time()
        p.current_loc_enter = t
        self.points.append(p)
        self.is_visiting.append(p.get_next_target().loc != self)
        p.set_current_location(self, t)
        self.set_movement_method(p)

        if p.latched_to is None:
            latched_text = ''
        else:
            latched_text = f' latched with {p.latched_to.ID}'
        Logger.log(f"Entered {p.ID} to {self.name} using {p.current_trans}{latched_text}. [{p.get_next_target()}].", 'd')

        current_loc_leave = self.get_leaving_time(p, t)
        is_visiting = True
        # if p.get_current_location() is None:  # initialize
        #     pass

        if p.get_next_target().loc == self:
            is_visiting = False
            if p.current_target_idx == len(p.route) - 1 and p.route[-1].loc == self:
                p.is_day_finished = True
                Logger.log(f"{self.ID} finished daily route!", 'c')
            else:
                p.increment_target_location()
            current_loc_leave = self.get_leaving_time(p, t)  # new leaving time after incrementing target
        elif p.get_current_target().loc == self:
            pass
        else:
            # next_location = MovementEngine.find_next_location(p)
            # p.set_point_destination(next_location)
            current_loc_leave = t - 1
        p.current_loc_leave = current_loc_leave

        # following lines should be always after the above code
        p.on_enter_location(self, t)  # transporters try to latch others here

        if self.capacity is not None:
            if self.capacity < len(self.is_visiting) - sum(self.is_visiting):
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
                               f"Staying:{len(self.is_visiting) - sum(self.is_visiting)} "
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

    def set_movement_method(self, p):
        if not p.latched_to:
            # add the person to the default transportation system, if the person is not latched to someone else.
            trans = p.main_trans
            if self.override_transport is not None and not isinstance(p, Transporter):
                if self.override_transport.override_level <= p.main_trans.override_level:
                    trans = self.override_transport
            trans.add_point_to_transport(p)

    def get_leaving_time(self, p, t):
        # if p.route[p.current_target_idx].duration_time != -1:
        #     current_loc_leave = min(t + p.route[p.current_target_idx].duration_time, t - t % Time.DAY + Time.DAY - 1)
        # else:

        current_loc_leave = p.route[p.current_target_idx].leaving_time % Time.DAY + t - t % Time.DAY
        if p.is_day_finished and self == p.home_loc:
            if current_loc_leave < t - t % Time.DAY + Time.DAY:
                current_loc_leave += Time.DAY
        return current_loc_leave

    def remove_point(self, point):
        idx = self.points.index(point)
        self._remove_point(idx)

    def _remove_point(self, idx):
        self.points.pop(idx)
        self.is_visiting.pop(idx)

    def is_inside(self, x, y):
        # if self.shape == Shape.POLYGON.value:
        #     return is_inside_polygon(self.boundary, (x, y))
        # if self.shape == Shape.CIRCLE.value:
        return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.radius ** 2

    def is_intersecting(self, x, y, r, eps=0):
        _is = False
        for l in self.locations:
            if l.shape == Shape.CIRCLE.value:
                if (l.x - x) ** 2 + (l.y - y) ** 2 < r ** 2 + l.radius ** 2 - eps ** 2:
                    _is = True
                    break
            # todo other shapes
        return _is
