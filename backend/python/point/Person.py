import numpy as np

from backend.python.Logger import Logger
from backend.python.Time import Time
from backend.python.enums import State
from backend.python.functions import find_in_subtree, get_random_element


class Person:
    normal_temperature = (36.8, 1.0)
    infect_temperature = (37.4, 1.2)
    _id = 0
    all_people = []
    all_positions = np.zeros((0, 2))
    all_velocities = np.zeros((0, 2))

    all_movement_ids = np.array([], dtype=int)
    all_movement_enter_times = np.array([], dtype=int)
    all_sources = np.array([], dtype=int)
    all_destinations = np.array([], dtype=int)
    all_destination_exits = np.array(np.zeros((0, 2)), dtype=int)

    all_current_loc_positions = np.zeros((0, 2))
    all_current_loc_radii = np.array([], dtype=int)
    all_current_loc_vcap = np.array([], dtype=int)

    n_characteristics = 3

    def __init__(self):
        self.ID = Person._id
        Person._id += 1

        self.gender = 0 if np.random.rand() < 0.5 else 1  # gender of the person
        self.age = np.random.uniform(1, 80)  # age todo add to repr
        self.immunity = 1 / self.age if np.random.rand() < 0.9 else np.random.rand()  # todo find and add to repr
        self.character_vector = np.zeros((Person.n_characteristics,))  # characteristics of the point
        self.behaviour = 0.5  # behaviour of the point (healthy medical practices -> unhealthy)

        Person.all_positions = np.concatenate([Person.all_positions, [[0, 0]]], 0)
        Person.all_velocities = np.concatenate([Person.all_velocities, [[0, 0]]], 0)

        Person.all_movement_ids = np.append(Person.all_destinations, -1)
        Person.all_movement_enter_times = np.append(Person.all_destinations, -1)
        Person.all_sources = np.append(Person.all_destinations, -1)
        Person.all_destinations = np.append(Person.all_destinations, -1)
        Person.all_destination_exits = np.concatenate([Person.all_destination_exits, [[0, 0]]], 0)

        Person.all_current_loc_positions = np.concatenate([Person.all_current_loc_positions, [[0, 0]]], 0)
        Person.all_current_loc_radii = np.append(Person.all_current_loc_radii, 0)
        Person.all_current_loc_vcap = np.append(Person.all_current_loc_vcap, 0)

        self._backup_route = None
        self._backup_duration_time = None
        self._backup_leaving_time = None
        self._backup_likely_trans = None

        self.is_day_finished = False

        self.route = []  # route that point is going to take. (list of location refs)
        self.current_target_idx = -1  # current location in the route (index of the route list)
        self.current_loc_enter = -1
        self.current_loc_leave = -1

        self.home_loc = None
        self.home_weekend_loc = None
        self.work_loc = None
        self.current_loc = None

        self.main_trans = None  # main transport medium the point will use
        self.current_trans = None

        self.in_inter_trans = False
        self.latched_to = None
        self.latch_onto_hash = None

        self.state = State.SUSCEPTIBLE.value  # current state of the point (infected/dead/recovered etc.)

        self.source = None  # infected source point
        self.infected_time = -1  # infected time
        self.infected_location = None  # infected location (ID)
        self.disease_state = 0  # disease state, higher value means bad for the patient # todo add to repr

        self.tested_positive_time = -1  # tested positive time

        self.temp = 0  # temperature of the point
        self.update_temp(0.0)
        Person.all_people.append(self)

    def __repr__(self):
        d = self.get_description_dict()
        return ','.join(map(str, d.values()))

    def __str__(self):
        return str(self.ID)

    def get_description_dict(self):
        d = {'class': self.__class__.__name__, 'id': self.ID,
             'x': self.all_positions[self.ID][0], 'y': self.all_positions[self.ID][0],
             'vx': self.all_velocities[self.ID][0], 'vy': self.all_velocities[self.ID][1],
             'state': self.state, 'gender': self.gender, 'is_day_finished': self.is_day_finished,
             'current_target_idx': self.current_target_idx, 'current_loc_enter': self.current_loc_enter,
             'current_loc_leave': self.current_loc_leave, 'in_inter_trans': self.in_inter_trans,
             'wealth': self.character_vector,
             'behaviour': self.behaviour, 'infected_time': self.infected_time, 'temp': self.temp,
             "tested_positive_time": self.tested_positive_time}

        if self.current_loc is None:
            d['current_loc_id'] = -1
        else:
            d['current_loc_id'] = self.current_loc.ID
        if self.main_trans is None:
            d['main_trans_id'] = -1
        else:
            d['main_trans_id'] = self.main_trans.ID
        if self.current_trans is None:
            d['current_trans_id'] = -1
        else:
            d['current_trans_id'] = self.current_trans.ID

        if self.source is None:
            d['source_id'] = -1
        else:
            d['source_id'] = self.source.ID

        if self.infected_location is None:
            d['infected_location_id'] = -1
        else:
            d['infected_location_id'] = self.infected_location.ID

        return d

    def initialize_character_vector(self, vec):
        self.character_vector = vec

    def get_character_transform_matrix(self):
        return np.random.random((Person.n_characteristics, Person.n_characteristics))

    def backup_route(self):
        if self._backup_route is None:
            self._backup_route = [r for r in self.route]

    def restore_route(self):
        if self._backup_route is not None:
            self.route = [r for r in self._backup_route]
            self._backup_route = None
            self.current_target_idx = len(self.route) - 1

    def reset_day(self, t):
        if self.get_current_location() != self.home_loc and not self.get_current_location().quarantined:
            Logger.log(
                f"{self.ID} {self.__class__.__name__} not at home when day resets. (Now at {self.get_current_location().name} "
                f"from {Time.i_to_time(self.all_movement_enter_times[self.ID])}) "
                f"CTarget {self.current_target_idx}/{len(self.route)} "
                f"Route {list(map(str, self.route))}. "
                f"{self.__repr__()}"

                , 'c')
            return False

        self.is_day_finished = False
        self.adjust_leaving_time(t)
        self.character_vector = np.dot(self.get_character_transform_matrix(), self.character_vector.T)
        return True

    def on_enter_location(self, t):
        pass

    def adjust_leaving_time(self, t):
        _t = t - t % Time.DAY
        for i in range(len(self.route)):
            if self.route[i].leaving_time == -1:
                continue
            if self.route[i].leaving_time < _t or self.route[i].leaving_time > _t + Time.DAY:
                self.route[i].leaving_time = self.route[i].leaving_time % Time.DAY + _t

    def increment_target_location(self):
        msg = f"{self.ID} incremented target from {self.get_current_target()} to "
        self.current_target_idx = (self.current_target_idx + 1) % len(self.route)
        from backend.python.MovementEngine import MovementEngine
        next_loc = MovementEngine.find_next_location(self)
        msg += f"{self.get_current_target()} ({self.current_target_idx}/{len(self.route)} target). Next location is {next_loc}."
        Logger.log(msg, 'i')
        if self.current_target_idx == 0:
            self.is_day_finished = True
            Logger.log(f"{self.ID} finished daily route!", 'c')

    def set_home_loc(self, home_loc):
        self.home_loc = home_loc
        self.route = self.home_loc.get_suggested_sub_route(self, [])
        self.route[0].enter_person(self)

    def find_closest(self, target, cur, find_from_level=-1):
        if target is None:
            return None
        # find closest (in tree) object to target
        if cur is None:
            cur = self.get_current_target().loc  # todo current target or current location
        possible_targets = []
        _possible = find_in_subtree(cur, target, None)
        if len(_possible) > 0:
            possible_targets.append(_possible)
        while cur.parent_location is not None:
            _possible = find_in_subtree(cur.parent_location, target, cur)
            if len(_possible) > 0:
                possible_targets.append(_possible)
                if len(possible_targets) == find_from_level:
                    break
            cur = cur.parent_location
        if len(possible_targets) == 0:
            raise Exception(f"Could not find {target} in the tree!!!")

        if find_from_level == -1:
            level = int(np.floor(np.random.exponential()))
            level = min(level, len(possible_targets) - 1)
        else:
            level = min(find_from_level - 1, len(possible_targets) - 1)

        if level > 0:
            Logger.log(f"{self} is going to {target} that is at level {level}", 'e')
        return get_random_element(possible_targets[level])

    def get_random_route_at(self, route_so_far, find_from_level):
        from backend.python.const import get_loc_for_p_at_t
        if len(route_so_far) == 0:
            t = 0
            cur = None
        else:
            t = route_so_far[-1].leaving_time
            cur = route_so_far[-1].loc

        cls_or_obj = get_loc_for_p_at_t(self, t)
        if len(cls_or_obj) == 0:  # no plan for this time
            return route_so_far
        target = get_random_element(cls_or_obj)
        if target is None:  # no plan for this time
            return route_so_far

        selected = self.find_closest(target, cur=cur, find_from_level=find_from_level)
        # if selected == cur:  # visiting the same location again is not valid
        #     return route_so_far
        route_so_far = selected.get_suggested_sub_route(self, route_so_far)

        return route_so_far

    def get_random_route_through(self, route_so_far, cls_or_obj, find_from_level):
        if len(route_so_far) == 0:
            t = 0
            cur = None
        else:
            t = route_so_far[-1].leaving_time
            cur = route_so_far[-1].loc

        for target in cls_or_obj:
            selected = self.find_closest(target, cur=cur, find_from_level=find_from_level)
            route_so_far = selected.get_suggested_sub_route(self, route_so_far)
        return route_so_far

    def get_random_route(self, end_at):
        route = []
        time = 0
        tries = 0
        while time < end_at:
            r_len = len(route)
            route = self.get_random_route_at(route, find_from_level=1)
            if len(route) == r_len:
                tries += 1

            if tries > 10:
                if len(route) == 1:
                    raise Exception()  # break due to not increasing route
                break

        return route

    def update_route(self, root, t, new_route_classes=None, replace=False):
        """
        update the route of the person from current position onwards.
        if new_route_classes are given, new route will be randomly selected suggested routes from those classes
        :param root:
        :param t:
        :param new_route_classes:
        :return:
        """
        if new_route_classes is None:
            return

        Logger.log(f"Current route for {self.ID} is {list(map(str, self.route))}", 'e')
        _t = t % Time.DAY
        self.backup_route()
        route, time = self.get_random_route_through(_t, new_route_classes, force_dt=True, cur=None, find_from_level=1)

        if replace:
            replace_from = 1
            # self.route = self.route[:1]
        else:
            replace_from = self.current_target_idx + 1
            # self.route = self.route[:self.current_target_idx + 1]

        # todo make sure current_target_idx is consistent with route
        new_route = self.route[:replace_from]
        while len(self.route) > replace_from and time > self.route[replace_from].leaving_time:
            replace_from += 1

        new_route += route + self.route[replace_from:]

        self.route = new_route
        self.adjust_leaving_time(t)

        Logger.log(f"Route updated for {self.ID} as {list(map(str, self.route))}", 'e')

        if self.latched_to:
            Logger.log(f"{self.ID} is latched to {self.latched_to.ID}. "
                       f"Delatching at {self.get_current_location().name}!", 'e')
            self.latched_to.delatch(self)

        if self.current_target_idx >= len(self.route):
            self.current_target_idx = len(route) - 1
        if replace:
            self.route[0].enter_person(self, target_location=None)

    def set_route(self, route, t, move2first=True):
        self.set_position(route[0].loc.x + np.random.normal(0, 1),
                          route[0].loc.y + np.random.normal(0, 1), True)
        self.route = route
        self.current_target_idx = 0
        if move2first:
            self.route[0].enter_person(self)

    def set_position(self, new_x, new_y, force=False):
        if not self.latched_to or force:
            self.all_positions[self.ID] = [new_x, new_y]
        else:
            start = self.all_movement_enter_times[self.ID]
            raise Exception(f"Tried to move {self.ID} in {self.get_current_location()} (enter at:{start})."
                            f"Going to {self.get_next_target()}")

    def set_current_location(self, loc, t):
        self.current_loc = loc
        Person.all_current_loc_positions[self.ID] = loc.x, loc.y
        Person.all_current_loc_radii[self.ID] = loc.radius

    def get_current_location(self):
        return self.current_loc

    def get_current_target(self):
        return self.route[self.current_target_idx]

    def get_next_target(self):
        return self.route[(self.current_target_idx + 1) % len(self.route)]

    def set_infected(self, t, p, common_p):
        self.state = State.INFECTED.value
        self.infected_time = t
        self.source = p
        self.infected_location = p.get_current_location()
        self.update_temp(common_p)
        self.disease_state = 1

    def set_recovered(self):
        self.state = State.RECOVERED.value
        self.restore_route()
        self.disease_state = 0

    def set_susceptible(self):
        self.state = State.SUSCEPTIBLE.value

    def set_dead(self):
        self.state = State.DEAD.value
        self.temp = 25
        self.all_velocities[self.ID] = [0, 0]

    def is_infected(self):
        return self.state == State.INFECTED.value

    def is_recovered(self):
        return self.state == State.RECOVERED.value

    def is_dead(self):
        return self.state == State.DEAD.value

    def is_susceptible(self):
        return self.state == State.SUSCEPTIBLE.value

    def is_tested_positive(self):
        return self.tested_positive_time > 0

    def update_temp(self, common_p):
        if self.is_infected():
            self.temp = np.random.normal(*Person.infect_temperature)
        elif self.is_recovered() or self.is_susceptible():
            if np.random.rand() < common_p:  # Common fever
                self.temp = np.random.normal(*Person.infect_temperature)
            else:
                self.temp = np.random.normal(*Person.normal_temperature)
        elif self.is_dead():
            self.temp = 25
