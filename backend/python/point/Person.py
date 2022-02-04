import numpy as np

from backend.python.CovEngine import CovEngine
from backend.python.Logger import Logger
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Time import Time
from backend.python.enums import State, ClassNameMaps, PersonFeatures, PersonOcc
from backend.python.functions import find_in_subtree, get_random_element


class Person:
    normal_temperature = (36.8, 1.0)
    infect_temperature = (37.4, 1.2)
    _id = 0
    all_people = []
    features = np.zeros((0, len(PersonFeatures) + 1))
    roster_ratio = 3/7
    # all_positions = np.zeros((0, 2))
    # all_velocities = np.zeros((0, 2))

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
        self.class_name = self.__class__.__name__
        self.ID = Person._id
        Person._id += 1

        tmp_feature_arr = np.zeros(len(PersonFeatures) + 1)
        tmp_feature_arr[PersonFeatures.id.value] = self.ID
        tmp_feature_arr[PersonFeatures.occ.value] = PersonOcc[self.__class__.__name__].value
        tmp_feature_arr[PersonFeatures.gender.value] = 0 if np.random.rand() < 0.5 else 1  # gender of the person
        tmp_feature_arr[PersonFeatures.age.value] = self.initialize_age()
        tmp_feature_arr[PersonFeatures.base_immunity.value] = 1 / tmp_feature_arr[
            PersonFeatures.age.value] if np.random.rand() < 0.9 else np.random.rand()  # todo find
        tmp_feature_arr[PersonFeatures.immunity_boost.value] = 0
        tmp_feature_arr[
            PersonFeatures.behaviour.value] = 0.5  # behaviour of the point (healthy medical practices -> unhealthy)
        tmp_feature_arr[PersonFeatures.asymptotic_chance.value] = tmp_feature_arr[
                                                                      PersonFeatures.base_immunity.value] ** 2
        tmp_feature_arr[PersonFeatures.is_asymptotic.value] = -1
        tmp_feature_arr[PersonFeatures.social_d.value] = 0.0
        tmp_feature_arr[PersonFeatures.hygiene_p.value] = 1.0
        tmp_feature_arr[PersonFeatures.temp.value] = 35
        tmp_feature_arr[PersonFeatures.state.value] = State.SUSCEPTIBLE.value
        tmp_feature_arr[PersonFeatures.disease_state.value] = 0
        tmp_feature_arr[PersonFeatures.source_id.value] = -1
        tmp_feature_arr[PersonFeatures.inf_t.value] = -1
        tmp_feature_arr[PersonFeatures.inf_l.value] = -1
        tmp_feature_arr[PersonFeatures.tested_t.value] = -1
        tmp_feature_arr[PersonFeatures.px.value] = -1
        tmp_feature_arr[PersonFeatures.py.value] = -1
        tmp_feature_arr[PersonFeatures.vx.value] = -1
        tmp_feature_arr[PersonFeatures.vy.value] = -1
        tmp_feature_arr[PersonFeatures.fr.value] = -1
        tmp_feature_arr[PersonFeatures.to.value] = -1
        tmp_feature_arr[PersonFeatures.tox.value] = -1
        tmp_feature_arr[PersonFeatures.toy.value] = -1
        tmp_feature_arr[PersonFeatures.cl_id.value] = -1
        tmp_feature_arr[PersonFeatures.cl_enter_t.value] = -1
        tmp_feature_arr[PersonFeatures.cl_leave_t.value] = -1
        tmp_feature_arr[PersonFeatures.cl_x.value] = -1
        tmp_feature_arr[PersonFeatures.cl_y.value] = -1
        tmp_feature_arr[PersonFeatures.cl_r.value] = -1
        tmp_feature_arr[PersonFeatures.cl_v_cap.value] = -1
        tmp_feature_arr[PersonFeatures.day_over.value] = 0
        tmp_feature_arr[PersonFeatures.home_id.value] = -1
        tmp_feature_arr[PersonFeatures.home_w_id.value] = -1
        tmp_feature_arr[PersonFeatures.work_id.value] = -1
        tmp_feature_arr[PersonFeatures.cm_id.value] = -1
        tmp_feature_arr[PersonFeatures.cm_enter_t.value] = -1
        tmp_feature_arr[PersonFeatures.fm_id.value] = -1
        tmp_feature_arr[PersonFeatures.is_transporter.value] = 0
        tmp_feature_arr[PersonFeatures.latched_id.value] = -1

        tmp_feature_arr[PersonFeatures.base_happiness.value] = 50
        tmp_feature_arr[PersonFeatures.happiness.value] = tmp_feature_arr[PersonFeatures.base_happiness.value]
        tmp_feature_arr[PersonFeatures.social_class.value] = 5

        tmp_feature_arr[PersonFeatures.daily_income.value] = 1500
        tmp_feature_arr[PersonFeatures.economic_status.value] = 1000

        Person.features = np.append(Person.features, np.expand_dims(tmp_feature_arr, 0), axis=0)

        # self.gender = 0 if np.random.rand() < 0.5 else 1  # gender of the person
        # self.age = self.initialize_age()
        # self.base_immunity = 1 / self.age if np.random.rand() < 0.9 else np.random.rand()  # todo find
        # self.immunity_boost = 0
        self.character_vector = np.zeros((Person.n_characteristics,))  # characteristics of the point
        # self.behaviour = 0.5  # behaviour of the point (healthy medical practices -> unhealthy)
        # self.asymptotic_chance = self.base_immunity ** 2
        # self.is_asymptotic = False

        # self.happiness = 50  # happiness score 0 to 100
        # self.social_class = 5  # social class 0 to 10, 0 mean lowest (poor) 10 mean highest (rich)
        # self.daily_income = 1500
        # self.daily_expense = 800

        # Person.all_positions = np.concatenate([Person.all_positions, [[0, 0]]], 0)
        # Person.all_velocities = np.concatenate([Person.all_velocities, [[0, 0]]], 0)

        Person.all_movement_ids = np.append(Person.all_movement_ids, -1)
        Person.all_movement_enter_times = np.append(Person.all_movement_enter_times, -1)
        Person.all_sources = np.append(Person.all_sources, -1)
        Person.all_destinations = np.append(Person.all_destinations, -1)
        Person.all_destination_exits = np.concatenate([Person.all_destination_exits, [[0, 0]]], 0)

        Person.all_current_loc_positions = np.concatenate([Person.all_current_loc_positions, [[0, 0]]], 0)
        Person.all_current_loc_radii = np.append(Person.all_current_loc_radii, 0)
        Person.all_current_loc_vcap = np.append(Person.all_current_loc_vcap, 0)

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

        # self.in_inter_trans = False
        self.latched_to = None
        self.latch_onto_hash = None

        # self.state = State.SUSCEPTIBLE.value  # current state of the point (infected/dead/recovered etc.)

        self.source = None  # infected source point
        self.infected_time = -1  # infected time
        self.infected_location = None  # infected location
        self.disease_state = 0  # disease state, higher value means bad for the patient # todo add to repr

        self.tested_positive_time = -1  # tested positive time
        self.last_tested_time = -1

        self.roster_days = []#[i for i in range(7) if np.random.rand() < Person.roster_ratio]
        self.is_roster_day = True

        # self.social_distance = 0.0
        # self.hygeinic_p = 1.0  # TODO

        # self.temp = 0  # temperature of the point
        self.update_temp(0.0)
        Person.all_people.append(self)

    def __repr__(self):
        d = self.get_description_dict()
        return ','.join(map(str, d.values()))

    def __str__(self):
        return str(self.ID)

    def print(self):
        d = self.get_description_dict()
        for key in d.keys():
            print(key, d[key])
        d = self.get_fine_description_dict(Time.get_time())
        for key in d.keys():
            print(key, d[key])

    def get_description_dict(self):
        d = {'person': self.ID,
             'person_class': ClassNameMaps.pc_map[self.class_name],
             'gender': self.features[self.ID, PersonFeatures.gender.value],
             'age': self.features[self.ID, PersonFeatures.age.value],
             'base_immunity': self.features[self.ID, PersonFeatures.base_immunity.value],
             'immunity_boost': self.features[self.ID, PersonFeatures.immunity_boost.value],
             'behaviour': self.features[self.ID, PersonFeatures.behaviour.value],
             'happiness': self.features[self.ID, PersonFeatures.happiness.value],
             'base_happiness': self.features[self.ID, PersonFeatures.base_happiness.value],
             'social_class': self.features[self.ID, PersonFeatures.social_class.value],
             'daily_income': self.features[self.ID, PersonFeatures.daily_income.value],
             'economic_status': self.features[self.ID, PersonFeatures.economic_status.value],
             'character_vector': self.character_vector,

             'route': ' '.join(
                 map(str, RoutePlanningEngine.convert_route_to_occupancy_array(self.route, ClassNameMaps.lc_map, 5))),
             'route_len': len(self.route),

             'home_loc': self.home_loc.ID,
             'home_weekend_loc': self.home_weekend_loc.ID if self.home_weekend_loc is not None else -1,
             'work_loc': self.work_loc.ID if self.work_loc is not None else -1,
             'main_trans': ClassNameMaps.mc_map[self.main_trans.class_name] if self.main_trans is not None else -1,

             'state': self.features[self.ID, PersonFeatures.state.value],
             'disease_state': self.disease_state,
             'infected_time': self.infected_time,
             'infected_source_class': ClassNameMaps.pc_map[self.source.class_name] if self.source is not None else -1,
             'infected_source_id': self.source.ID if self.source is not None else -1,
             'infected_loc_class': ClassNameMaps.lc_map[
                 self.infected_location.class_name] if self.infected_location is not None else -1,
             'infected_loc_id': self.infected_location.ID if self.infected_location is not None else -1,
             'is_asymptotic': int(self.is_asymptotic) if self.is_infected() else -1,
             'tested_positive_time': self.tested_positive_time,
             'temp': self.features[self.ID, PersonFeatures.temp.value],
             }

        return d

    def get_fine_description_dict(self, mins):
        d = {
            'person': self.ID,
            'person_class': ClassNameMaps.pc_map[self.class_name],  # redundant
            'current_location_id': self.get_current_location().ID if self.get_current_location() is not None else -1,
            'current_location_class': ClassNameMaps.lc_map[self.get_current_location().class_name],
            'current_movement_id': self.current_trans.ID if self.current_trans is not None else -1,
            'current_movement_class': ClassNameMaps.mc_map[self.current_trans.class_name],
            'cur_tar_idx': len(self.route) - 1 if self.is_day_finished else self.current_target_idx,
            'route_len': len(self.route),
            'time': mins,
            'is_day_finished': int(self.is_day_finished),

            'current_loc_enter': self.current_loc_enter,
            'current_loc_leave': self.current_loc_leave,
            'destination': self.all_destinations[self.ID],

            'x': round(self.features[self.ID, PersonFeatures.px.value] * 100) / 100,
            'y': round(self.features[self.ID, PersonFeatures.py.value] * 100) / 100,

            'vx': self.features[self.ID, PersonFeatures.vx.value],
            'vy': self.features[self.ID, PersonFeatures.vx.value],

        }
        return d

    def initialize_age(self):
        raise NotImplementedError()

    def initialize_character_vector(self, vec):
        self.character_vector = vec

    def get_character_transform_matrix(self):
        return np.random.random((Person.n_characteristics, Person.n_characteristics))

    def reset_day(self, t):
        ret = True
        from backend.python.point.Transporter import Transporter
        if self.get_current_location() != self.home_loc and self.get_current_location() != self.home_weekend_loc and \
                not self.get_current_location().quarantined and not isinstance(self,
                                                                               Transporter) and not self.is_dead():
            Logger.log(
                f"{self.ID} {self.__class__.__name__} not at home when day resets. (Now at {self.get_current_location().name} "
                f"from {Time.i_to_time(self.all_movement_enter_times[self.ID])} next target {self.get_next_target().loc.name}) "
                f"CTarget {self.current_target_idx}/{len(self.route) - 1} "
                f"Route {list(map(str, self.route))}. "
                f"{self.__repr__()}"

                , 'c')
            # self.print()
            ret = False

        # removing all latched people from transporters because we can't have them
        # inside a transporter when resetting the day
        if isinstance(self, Transporter):
            self.force_delatch_and_teleport_all()

        self.is_day_finished = False
        self.current_target_idx = 0
        self.is_roster_day = t//Time.DAY//7 in self.roster_days

        from backend.python.RoutePlanningEngine import RoutePlanningEngine

        RoutePlanningEngine.set_route(self, t)
        # self.adjust_leaving_time(t)
        self.character_vector = np.dot(self.get_character_transform_matrix(), self.character_vector.T)
        self.features[self.ID, PersonFeatures.immunity_boost.value] *= CovEngine.daily_immunity_boost_dec_factor
        return ret

    def on_enter_location(self, loc, t):
        pass

    def on_enter_home(self):
        pass

    def adjust_leaving_time(self, t):
        _t = t - t % Time.DAY
        for i in range(len(self.route)):
            if self.route[i].leaving_time < _t or self.route[i].leaving_time > _t + Time.DAY:
                self.route[i].set_leaving_time(self.route[i].leaving_time % Time.DAY + _t)

    def increment_target_location(self):
        msg = f"{self.ID} incremented target from {self.get_current_target()} to "
        if self.current_target_idx + 1 < len(self.route):
            self.current_target_idx = (self.current_target_idx + 1) % len(self.route)
        from backend.python.MovementEngine import MovementEngine
        next_loc = MovementEngine.find_next_location(self)
        msg += f"{self.get_current_target()} ({self.current_target_idx}/{len(self.route)} target). Next location is {next_loc}."
        Logger.log(msg, 'i')

    def set_home_loc(self, home_loc):
        self.home_loc = home_loc
        self.route = self.home_loc.get_suggested_sub_route(self, [])
        self.route[0].enter_person(self)

    def find_closest(self, target, cur, find_from_level=0):  # todo optimize this
        if target is None:
            return None
        if type(target) != type and type(target) != str:  # why are u searching for a loc if u know the loc?
            return target
        # find closest (in tree) object to target
        if cur is None:
            cur = self.get_current_target().loc  # todo current target or current location
        possible_targets = []
        _possible = find_in_subtree(cur, target, None)
        if len(_possible) > 0:
            possible_targets.append(_possible)
        while cur.parent_location is not None:
            if find_from_level >= 0 and len(possible_targets) == find_from_level + 1:
                break

            _possible = find_in_subtree(cur.parent_location, target, cur)
            if len(_possible) > 0:
                possible_targets.append(_possible)
            cur = cur.parent_location
        if len(possible_targets) == 0:
            # raise Exception(f"Could not find {target} in the tree!!!")
            Logger.log(f"Could not find {target} in the tree!!!", 'c')
            return self.home_loc

        if find_from_level < 0:
            level = int(np.floor(np.random.exponential()))
            level = min(level, len(possible_targets) - 1)
        else:
            level = min(find_from_level, len(possible_targets) - 1)

        if level > 0:
            Logger.log(f"{self} is going to {target} that is at level {level}", 'd')
        return get_random_element(possible_targets[level])

    def get_random_route_at(self, route_so_far, find_from_level):
        if len(route_so_far) == 0:
            t = Time.get_time()
            cur = None
        else:
            t = route_so_far[-1].leaving_time
            cur = route_so_far[-1].loc
        if len(route_so_far) > 1:
            route_so_far = RoutePlanningEngine.optimize_route(route_so_far)
        cls_or_obj = RoutePlanningEngine.get_loc_for_p_at_t(route_so_far, self, t)
        if len(cls_or_obj) == 0:  # no plan for this time
            return route_so_far
        target = get_random_element(cls_or_obj)
        if target is None:  # no plan for this time
            return route_so_far

        return self.get_random_route_through(route_so_far, [target], find_from_level)

    def get_random_route_through(self, route_so_far, cls_or_obj, find_from_level):
        if len(route_so_far) == 0:
            t = Time.get_time()
            cur = None
        else:
            t = route_so_far[-1].leaving_time
            cur = route_so_far[-1].loc

        for target in cls_or_obj:
            selected = self.find_closest(target, cur=cur, find_from_level=find_from_level)
            # if selected == cur:  # visiting the same location again is not valid
            #     return route_so_far
            route_so_far = selected.get_suggested_sub_route(self, route_so_far)
        return route_so_far

    def get_random_route(self, t, end_at):
        route = []

        tries = 0
        while t < end_at:
            r_len = len(route)
            route = self.get_random_route_at(route, find_from_level=1)
            t = route[-1].leaving_time
            # if len(route) == r_len:
            #     tries += 1
            # if tries > 5 and len(route) == 1:
            #     pass
            # if tries > 10:
            #     if len(route) == 1:
            #         raise Exception()  # break due to not increasing route
            #     break

        return route

    def update_route(self, root, t, new_route_classes=None, replace=False):
        """
        update the route of the person from current position onwards.
        if new_route_classes are given, new route will be randomly selected suggested routes from those classes
        """
        if new_route_classes is None:
            return

        Logger.log(f"Current route for {self.ID} is {list(map(str, self.route))}", 'e')
        _t = t % Time.DAY

        if replace:
            replace_from = 1
        else:
            replace_from = self.current_target_idx + 1
        route_so_far = self.route[:replace_from]
        route_so_far = self.get_random_route_through(route_so_far, new_route_classes, find_from_level=-1)

        # todo make sure current_target_idx is consistent with route
        # while len(self.route) > replace_from and time > self.route[replace_from].leaving_time:
        #     replace_from += 1

        self.set_route(route_so_far, t, move2first=replace)
        # self.adjust_leaving_time(t)

        Logger.log(f"Route updated for {self.ID} as {list(map(str, self.route))}", 'e')

        if self.latched_to:
            Logger.log(f"{self.ID} is latched to {self.latched_to.ID}. "
                       f"Delatching at {self.get_current_location().name}!", 'e')
            self.latched_to.delatch(self)

        if self.current_target_idx >= len(self.route):
            self.current_target_idx = len(self.route) - 1

    def set_route(self, route, t, move2first=True):

        route = RoutePlanningEngine.optimize_route(route)
        if not self.is_tested_positive():
            if route[0].loc != self.home_loc and route[0].loc != self.home_weekend_loc:
                raise Exception("Initial location invalid!")
            if route[-1].loc != self.home_loc and route[-1].loc != self.home_weekend_loc:
                raise Exception("Last location invalid!")
        self.route = route
        if move2first:
            self.current_target_idx = 0
            x = route[0].loc.px + np.random.normal(0, 1)
            y = route[0].loc.py + np.random.normal(0, 1)
            self.set_position(x, y, True)
            self.route[0].enter_person(self)

    def set_position(self, new_x, new_y, force=False):
        if not self.latched_to or force:
            self.features[self.ID, PersonFeatures.px.value] = new_x
            self.features[self.ID, PersonFeatures.py.value] = new_y
        else:
            start = self.all_movement_enter_times[self.ID]
            print(self.get_description_dict())
            raise Exception(f"Tried to move {self.ID} in {self.get_current_location()} (enter at:{start})."
                            f"Going to {self.get_next_target()}")

    def set_point_destination(self, target_location):
        if target_location is not None:
            _id = target_location.ID
        else:
            _id = -1
            target_location = self.get_current_location()

        Person.all_destinations[self.ID] = _id
        Person.all_destination_exits[self.ID] = [target_location.ex, target_location.ey]

    def get_point_destination(self):
        id = Person.all_destinations[self.ID]
        if id != -1:
            return self.get_current_location().all_locations[id]

    def set_current_location(self, loc, t):
        self.current_loc = loc
        r = loc.radius
        Person.all_current_loc_positions[self.ID] = loc.px - r, loc.py - r
        Person.all_current_loc_radii[self.ID] = r

    def get_current_location(self):
        return self.current_loc

    def get_current_target(self):
        return self.route[self.current_target_idx]

    def get_next_target(self):
        # if self.in_inter_trans:
        #     return self.route[self.current_target_idx]
        return self.route[min(self.current_target_idx + 1, len(self.route) - 1)]

    def get_effective_immunity(self):
        return min(1, max(0, self.features[self.ID, PersonFeatures.base_immunity.value] +
                          self.features[self.ID, PersonFeatures.immunity_boost.value] * (
                                  1 - self.features[self.ID, PersonFeatures.base_immunity.value])))

    def set_infected(self, t, p, common_p):
        self.features[self.ID, PersonFeatures.state.value] = State.INFECTED.value
        self.infected_time = t
        self.source = p
        self.infected_location = p.get_current_location()
        self.update_temp(common_p)
        self.disease_state = 1
        self.is_asymptotic = np.random.rand() < self.features[self.ID, PersonFeatures.asymptotic_chance.value]

    def set_recovered(self):
        self.features[self.ID, PersonFeatures.state.value] = State.RECOVERED.value
        self.disease_state = 0

    def set_susceptible(self):
        self.features[self.ID, PersonFeatures.state.value] = State.SUSCEPTIBLE.value

    def set_dead(self):
        self.features[self.ID, PersonFeatures.state.value] = State.DEAD.value
        self.features[self.ID, PersonFeatures.temp.value] = 25
        self.features[self.ID, PersonFeatures.vx.value] = 0
        self.features[self.ID, PersonFeatures.vy.value] = 0

    def set_tested_positive(self):
        pass

    def is_infected(self):
        return self.features[self.ID, PersonFeatures.state.value] == State.INFECTED.value

    def is_recovered(self):
        return self.features[self.ID, PersonFeatures.state.value] == State.RECOVERED.value

    def is_dead(self):
        return self.features[self.ID, PersonFeatures.state.value] == State.DEAD.value

    def is_susceptible(self):
        return self.features[self.ID, PersonFeatures.state.value] == State.SUSCEPTIBLE.value

    def is_tested_positive(self):
        return self.tested_positive_time > 0

    def update_temp(self, common_p):
        if self.is_infected():
            self.features[self.ID, PersonFeatures.temp.value] = np.random.normal(*Person.infect_temperature)
        elif self.is_recovered() or self.is_susceptible():
            if np.random.rand() < common_p:  # Common fever
                self.features[self.ID, PersonFeatures.temp.value] = np.random.normal(*Person.infect_temperature)
            else:
                self.features[self.ID, PersonFeatures.temp.value] = np.random.normal(*Person.normal_temperature)
        elif self.is_dead():
            self.features[self.ID, PersonFeatures.temp.value] = 25
