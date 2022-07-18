from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target

from backend.python.enums import *
from backend.python.Time import Time
import numpy as np
import pandas as pd
from backend.python.point.Transporter import Transporter
from backend.python.transport.Movement import Movement


class Location:
    DEBUG = False
    all_locations = []
    _id = 0
    # features = np.zeros((0, len(LocationFeatures)+1))
    class_df = pd.read_csv('../python/data/location_classes.csv').reset_index()

    def __init__(self, class_info, spawn_sub=True, **kwargs):
        self.class_name = class_info['l_class']
        self.ID = Location._id
        Location._id += 1
        # tmp_feature_arr = np.zeros(len(LocationFeatures) + 1)
        # tmp_feature_arr[LocationFeatures.id] = self.ID
        # tmp_feature_arr[LocationFeatures.px] = x
        # tmp_feature_arr[LocationFeatures.py] = y
        # tmp_feature_arr[LocationFeatures.shape] = shape
        # tmp_feature_arr[LocationFeatures.depth] = 0
        # tmp_feature_arr[LocationFeatures.capacity] = kwargs.get('capacity')
        # tmp_feature_arr[LocationFeatures.infectious] = default_infectiousness[self.__class__] if kwargs.get(
        #     'infectiousness') is None else kwargs.get('infectiousness')
        # tmp_feature_arr[LocationFeatures.social_distance] = 0.0
        # tmp_feature_arr[LocationFeatures.hygiene_boost] = 0  # TODO
        # tmp_feature_arr[LocationFeatures.recovery_p] = 0.1  # TODO
        # tmp_feature_arr[LocationFeatures.quarantined] = kwargs.get('quarantined', 0)
        # tmp_feature_arr[LocationFeatures.quarantined_time] = -1
        # tmp_feature_arr[LocationFeatures.parent_id] = -1
        # tmp_feature_arr[LocationFeatures.om] = -1
        self.px = kwargs.get('x')
        self.py = kwargs.get('y')
        self.shape = kwargs.get('shape', Shape_CIRCLE)
        self.radius = kwargs.get('r', np.random.randint(class_info['r_min'], class_info['r_max']))
        exit_dist = kwargs.get('exitdist', 0.9)
        exit_theta = kwargs.get('exittheta', 0.0)

        if self.shape == Shape_CIRCLE:

            # tmp_feature_arr[LocationFeatures.radius] = kwargs.get('r')
            self.ex = self.px + np.cos(exit_theta) * self.radius * exit_dist
            self.ey = self.py + np.sin(exit_theta) * self.radius * exit_dist
            # tmp_feature_arr[LocationFeatures.ex] = x + np.cos(exit_theta) * kwargs.get('r') * exit_dist
            # tmp_feature_arr[LocationFeatures.ey] = y + np.sin(exit_theta) * kwargs.get('r') * exit_dist
        elif self.shape == Shape_POLYGON:
            self.boundary = kwargs.get('boundary')
            if self.boundary is None:
                raise Exception("Please provide boundary")
            # TODO add exit point here
            # tmp_feature_arr[LocationFeatures.px] = np.average(self.boundary[:, 0])
            # tmp_feature_arr[LocationFeatures.px] = np.average(self.boundary[:, 1])
            # tmp_feature_arr[LocationFeatures.ex] = tmp_feature_arr[LocationFeatures.px] * (1 - exit_dist) + \
            #                                              self.boundary[0][0] * exit_dist
            # tmp_feature_arr[LocationFeatures.ey] = tmp_feature_arr[LocationFeatures.py] * (1 - exit_dist) + \
            #                                              self.boundary[0][1] * exit_dist
            self.px = np.average(self.boundary[:, 0])
            self.py = np.average(self.boundary[:, 1])
            self.ex = self.px * (1 - exit_dist) + self.boundary[0][0] * exit_dist
            self.ey = self.py * (1 - exit_dist) + self.boundary[0][1] * exit_dist

        # Location.features = np.append(Location.features, np.expand_dims(tmp_feature_arr, 0), axis=0)

        self.depth = 0
        self.capacity = kwargs.get('capacity')
        self.recovery_p = kwargs.get('recovery_p', class_info['recovery_p'])  # todo find this, add to repr

        self.infectious = kwargs.get('infectiousness', class_info['infectiousness'])
        self.social_distance = kwargs.get('social_distance', class_info['social_distance'])
        self.hygiene_boost = kwargs.get('hygiene_boost', 0)
        self.happiness_boost = kwargs.get('happiness_boost', class_info['happiness_boost'])
        self.quarantined = kwargs.get('quarantined', False)
        self.quarantined_time = -1

        self.points = []
        self.is_visiting = []

        self.parent_location = None
        self.locations = []
        override_transport = class_info['override_transport']
        self.override_transport = None if pd.isna(override_transport) else Movement.all_instances[override_transport]
        self.name = kwargs.get('name', self.class_name[:3] + str(self.ID))
        Location.all_locations.append(self)

        if spawn_sub and not pd.isna(class_info['default_spawns']):
            for spawn_class in class_info['default_spawns'].split('|'):
                spawn_class_name, n_loc = spawn_class.split('#')
                n_loc = int(n_loc)
                spawn_class_info = Location.class_df.loc[Location.class_df['l_class'] == spawn_class_name].iloc[0]
                self.spawn_sub_locations(spawn_class_info, n_loc, **kwargs)

    def __repr__(self):
        d = self.get_description_dict()
        return ','.join(map(str, d.values()))

    def __str__(self):
        return self.name

    # def get_feature(self, feature):
    #     return self.features[self.ID, LocationFeatures[feature]]

    @staticmethod
    def get_location(_id):
        return Location.all_locations[int(_id)]

    def get_description_dict(self):
        d = {
            'class': ClassNameMaps.lc_map[self.class_name],
            'id': self.ID, 'x': self.px, 'y': self.py,
            'depth': self.depth, 'capacity': self.capacity,
            'override_transport': Movement.class_df.loc[Movement.class_df['m_class'] ==
                                                        self.override_transport.class_name].index[
                0] if self.override_transport is not None else -1,
            'infectious': self.infectious,
            'quarantined': 1 if self.quarantined else 0,
            'parent_id': self.parent_location.ID if self.parent_location is not None else -1,

            'children_ids': ' '.join([str(ch.ID) for ch in self.locations]),
            'quarantined_time': self.quarantined_time,
            'exit': ' '.join([str(e) for e in [self.ex, self.ey]]),
            'name': self.name,
        }

        if self.shape == Shape_CIRCLE:
            d['radius'] = self.radius
        elif self.shape == Shape_POLYGON:
            d['boundary'] = self.boundary.__str__().replace(',', '|').replace(' ', '')

        return d

    def spawn_sub_locations(self, class_info, n_sub_loc, spawn_sub=True, **kwargs):
        if n_sub_loc <= 0:
            return
        r_sub_loc = np.random.rand() * (int(class_info['r_max']) - int(class_info['r_min'])) + int(class_info['r_min'])
        cls = class_info['l_class']
        assert r_sub_loc > 0
        xs, ys = self.get_suggested_positions(n_sub_loc, r_sub_loc, cls)

        # print(f"Automatically creating {len(xs)}/{n_sub_loc} {cls} for {self.class_name} {self.name}")

        i = 0
        spawns = []
        for x, y in zip(xs, ys):
            # name = self.name + '-' + cls[:3] + str(i)
            if 'depth' not in kwargs.keys():
                kwargs['x'] = x
                kwargs['y'] = y
                # kwargs['name'] = name
            if cls == 'BusStation':
                from backend.python.location.Stations.BusStation import BusStation
                building = BusStation(class_info, spawn_sub, **kwargs)
            elif cls == 'TukTukStation':
                from backend.python.location.Stations.TukTukStation import TukTukStation
                building = TukTukStation(class_info, spawn_sub, **kwargs)
            else:
                building = Location(class_info, spawn_sub, **kwargs)
            self.add_sub_location(building)
            spawns.append(building)
            i += 1
        return spawns

    def get_suggested_positions(self, n, radius, cls_name):

        if self.shape == Shape_CIRCLE:
            possible_positions = []
            failed_positions = []
            x = self.px
            y = self.py
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
                while len(possible_positions) != n and len(failed_positions) > 0:
                    possible_positions.append(failed_positions.pop())
            else:
                possible_positions = possible_positions[:n]
            if len(possible_positions) < n:
                print(
                    f"Cannot make {n} {cls_name} locations with r={radius} inside {self.class_name} with r={self.radius}. "
                    f"Making only {len(possible_positions)} locations. Other points are random")
                while len(possible_positions) != n:
                    _theta = np.random.randint(0, 360) * (2 * np.pi) / 360
                    possible_positions.append((self.px + (r1 - r2) * np.random.rand() * np.cos(_theta),
                                               self.py + (r1 - r2) * np.random.rand() * np.sin(_theta)))

            idx = np.arange(len(possible_positions))
            np.random.shuffle(idx)
            x = [possible_positions[c][0] for c in idx]
            y = [possible_positions[c][1] for c in idx]

        elif self.shape == Shape_POLYGON:
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
        dur = RoutePlanningEngine.get_dur_for_p_in_loc_at_t(route_so_far, point, self, t)
        travel_time = MovementEngine.get_time_to_move(route_so_far[-1].loc, self, point) if len(route_so_far) > 0 else 0
        _r = [Target(self, t + dur + travel_time, None)]
        route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        return route_so_far

    def get_distance_to(self, loc):
        return ((self.px - loc.px) ** 2 + (self.py - loc.py) ** 2) ** 0.5

    def set_quarantined(self, quarantined, t, recursive=False):

        def f(r: Location):
            r.quarantined = quarantined
            Logger.log(f"{r.class_name} {r.name} ID={r.ID} quarantined={quarantined} at {t}", 'c')

            if quarantined:
                r.quarantined_time = t
            else:
                r.quarantined_time = -1
            if recursive:
                for ch in r.locations:
                    f(ch)

        f(self)

    def add_sub_location(self, location):
        # Location.features[location.ID, LocationFeatures.parent_id] = self.ID
        location.parent_location = self
        # Location.features[location.ID, LocationFeatures.depth] = Location.features[self.ID, LocationFeatures.depth] + 1
        location.depth = self.depth + 1
        self.locations.append(location)

        def f(ll):
            for ch in ll.locations:
                # Location.features[ch.ID, LocationFeatures.depth] = Location.features[ll.ID, LocationFeatures.depth] + 1
                ch.depth = ll.depth + 1
                f(ch)

        f(location)

    def leave_this_location(self, p, force=False):
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
        if (can_go_out_containment and can_go_out_movement) or force:
            p.set_point_destination(next_location)
            # Logger.log(f"{p.ID} move; {p.get_current_location()} -> {next_location} ({transporting_location}) [{p.get_next_target()}]",'d')
            transporting_location.enter_person(p)
        else:
            if not can_go_out_movement:
                MovementEngine.set_movement_method(transporting_location, p)
                # Logger.log(f"# {p} cannot leave {self} and goto {p.get_next_target()} (No transport) "
                #            f"Route:{p.current_target_idx}/{len(p.route)} (destination:{p.all_destinations[p.ID]})", 'c')
            # if not can_go_out_containment:
            #     Logger.log(f"# {p} cannot leave {self} and goto {p.get_next_target()} (Contained) "
            #                f"Route:{p.current_target_idx}/{len(p.route)}", 'd')

    def can_enter(self, p):
        from backend.python.transport.MovementByTransporter import MovementByTransporter
        if isinstance(p, Transporter):
            return True
        if p.latched_to is not None:
            return True

        # trans = MovementEngine.get_movement_method(self, p)
        # if p.current_trans != trans and p.current_trans != p.main_trans:
        #     # if we set a trans which is not the main trans and trans in loc, that means
        #     # we changed the trans manually to something like Taxi
        #     return True
        if self.override_transport is None and isinstance(p.main_trans,
                                                          MovementByTransporter):  # todo check this logic. add overriding levels
            return False
        return True

    def on_destination_reached(self, p):
        # Logger.log(f"Destination {self} reached by {p}", 'd')
        p.set_point_destination(None)
        self.enter_person(p)

    def enter_person(self, p):
        if p.get_current_location() is not None:
            p.get_current_location().remove_point(p)

        t = Time.get_time()
        p.current_loc_enter = t
        self.points.append(p)
        self.is_visiting.append(p.get_next_target().loc.ID != self.ID)
        p.set_current_location(self, t)

        if p.latched_to is None:
            latched_text = ''
        else:
            latched_text = f' latched with {p.latched_to.ID}'
        # Logger.log(f"Entered {p.ID} to {self.name} using {p.current_trans}{latched_text}. [{p.get_next_target()}].",
        #            'd')

        current_loc_leave = self.get_leaving_time(p, t)
        is_visiting = True
        # if p.get_current_location() is None:  # initialize
        #     pass

        if p.get_next_target().loc == self:
            is_visiting = False
            if p.current_target_idx == len(p.route) - 1 and p.route[-1].loc == self and p.is_day_finished == False:
                p.is_day_finished = True
                Logger.log(f"{self.ID} finished daily route!", 'd')
            else:
                p.increment_target_location()
            if p.is_day_finished:
                p.on_enter_home()
            current_loc_leave = self.get_leaving_time(p, t)  # new leaving time after incrementing target
        elif p.get_current_target().loc == self:
            pass
        else:
            # next_location = MovementEngine.find_next_location(p)
            # p.set_point_destination(next_location)
            current_loc_leave = t - 1
        p.current_loc_leave = current_loc_leave

        # following lines should be always after the above code
        MovementEngine.set_movement_method(self, p)
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

                    # Logger.log(f"CAPACITY reached on {self} when entering person {p.ID}! "
                    #            f"All:{len(self.is_visiting)} "
                    #            f"Visiting:{sum(self.is_visiting)} "
                    #            f"Staying:{len(self.is_visiting) - sum(self.is_visiting)} "
                    #            f"Capacity:{self.capacity}", 'e')
                    if self.parent_location is not None:
                        # next_location = MovementEngine.find_next_location(p)
                        # Logger.log(f"Person {p.ID} will be removed from current location {self} "
                        #            f"and it will be added to parent location {self.parent_location}"
                        #            f"to reach {next_location}.", 'c')
                        self.parent_location.enter_person(p)

                        # todo bug: if p is in home, when cap is full current_loc jump to self.parent
                        return  # don't add to this location because capacity reached
                    raise Exception("Capacity full at root node!!! Cannot handle this!")

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
        # if self.shape == Shape_POLYGON:
        #     return is_inside_polygon(self.boundary, (x, y))
        # if self.shape == Shape_CIRCLE:
        return (x - self.px) ** 2 + (y - self.py) ** 2 <= self.radius ** 2

    def is_intersecting(self, x, y, r, eps=0):
        _is = False
        for l in self.locations:
            if l.shape == Shape_CIRCLE:
                if (l.px - x) ** 2 + (l.py - y) ** 2 < r ** 2 + l.radius ** 2 - eps ** 2:
                    _is = True
                    break
            # todo other shapes
        return _is
