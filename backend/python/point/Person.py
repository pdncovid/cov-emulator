import numpy as np
import pandas as pd

from backend.python.CovEngine import CovEngine
from backend.python.Logger import Logger
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.enums import *
from backend.python.functions import find_in_subtree, get_random_element


class Person:
    normal_temperature = (36.8, 1.0)
    infect_temperature = (37.4, 1.2)
    _id = 0
    all_people = []
    features = np.zeros((0, len(PersonFeatures) + 1))
    roster_ratio = 3 / 7
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
    class_df = pd.read_csv('../python/data/person_classes.csv').reset_index()

    def __init__(self, class_info, **kwargs):
        self.class_name = class_info['p_class']
        self.ID = Person._id
        Person._id += 1

        _f_arr = np.zeros(len(PersonFeatures) + 1)
        _f_arr[PF_id] = self.ID
        _f_arr[PF_occ] = int(class_info['index'])
        _f_arr[PF_gender] = kwargs.get('gender', 0 if np.random.rand() < 0.5 else 1)
        _f_arr[PF_age] = kwargs.get('age', self.initialize_age(class_info['age_min'], class_info['age_max']))
        _f_arr[PF_base_immunity] = kwargs.get('base_immunity', 1 / (_f_arr[
                                                                        PF_age] + 1) if np.random.rand() < 0.9 else np.random.rand())  # todo find
        _f_arr[PF_immunity_boost] = kwargs.get('immunity_boost', 0)
        # _f_arr[PF_behaviour] = kwargs.get('behaviour', 0.5)
        _f_arr[PF_base_happiness] = kwargs.get('base_happiness', 50)
        _f_arr[PF_happiness] = kwargs.get('happiness', _f_arr[PF_base_happiness])
        _f_arr[PF_social_class] = kwargs.get('social_class', 5)
        _f_arr[PF_daily_income] = kwargs.get('daily_income', 1500)
        _f_arr[PF_economic_status] = kwargs.get('economic_status', 1000)
        _f_arr[PF_state] = kwargs.get('state', State_SUSCEPTIBLE)
        _f_arr[PF_disease_state] = kwargs.get('disease_state', DiseaseState_INCUBATION)
        _f_arr[PF_temp] = kwargs.get('temp', 35)
        _f_arr[PF_is_asymptotic] = kwargs.get('is_asymptotic', -1)
        _f_arr[PF_asymptotic_chance] = kwargs.get('asymptotic_chance', _f_arr[PF_base_immunity] ** 2)
        _f_arr[PF_hygiene_p] = kwargs.get('hygiene_p', class_info['hygiene_p'])

        _f_arr[PF_fm_id] = kwargs.get('fm_id', -1)

        _f_arr[PF_infected_source_id] = kwargs.get('infected_source_id', -1)
        _f_arr[PF_infected_time] = kwargs.get('infected_time', -1)
        _f_arr[PF_infected_loc_id] = kwargs.get('infected_loc_id', -1)
        _f_arr[PF_tested_positive_time] = kwargs.get('tested_positive_time', -1)

        _f_arr[PF_home_id] = kwargs.get('home_id', -1)
        _f_arr[PF_home_w_id] = kwargs.get('home_w_id', -1)
        _f_arr[PF_work_id] = kwargs.get('work_id', -1)

        _f_arr[PF_px] = kwargs.get('px', -1)
        _f_arr[PF_py] = kwargs.get('py', -1)
        _f_arr[PF_vx] = kwargs.get('vx', -1)
        _f_arr[PF_vy] = kwargs.get('vy', -1)
        # _f_arr[PF_fr] = kwargs.get('fr', -1)
        # _f_arr[PF_to] = kwargs.get('to', -1)
        # _f_arr[PF_tox] = kwargs.get('tox', -1)
        # _f_arr[PF_toy] = kwargs.get('toy', -1)

        # _f_arr[PF_cl_id] = kwargs.get('cl_id', -1)
        # _f_arr[PF_cl_enter_t] = kwargs.get('cl_enter_t', -1)
        # _f_arr[PF_cl_leave_t] = kwargs.get('cl_leave_t', -1)
        # _f_arr[PF_cl_x] = kwargs.get('cl_x', -1)
        # _f_arr[PF_cl_y] = kwargs.get('cl_y', -1)
        # _f_arr[PF_cl_r] = kwargs.get('cl_r', -1)
        # _f_arr[PF_cl_v_cap] = kwargs.get('cl_v_cap', -1)

        # _f_arr[PF_cm_id] = kwargs.get('cm_id', -1)
        # _f_arr[PF_cm_enter_t] = kwargs.get('cm_enter_t', -1)

        Person.features = np.append(Person.features, np.expand_dims(_f_arr, 0), axis=0)

        self.character_vector = np.zeros((Person.n_characteristics,))  # characteristics of the point

        Person.all_movement_ids = np.append(Person.all_movement_ids, -1)
        Person.all_movement_enter_times = np.append(Person.all_movement_enter_times, -1)
        Person.all_sources = np.append(Person.all_sources, -1)
        Person.all_destinations = np.append(Person.all_destinations, -1)
        Person.all_destination_exits = np.concatenate([Person.all_destination_exits, [[0, 0]]], 0)

        Person.all_current_loc_positions = np.concatenate([Person.all_current_loc_positions, [[0, 0]]], 0)
        Person.all_current_loc_radii = np.append(Person.all_current_loc_radii, 0)
        Person.all_current_loc_vcap = np.append(Person.all_current_loc_vcap, 0)

        # added to save load
        self.home_loc = None
        self.home_weekend_loc = None
        self.work_loc = None

        self.main_trans = None  # main transport medium the point will use

        # self.source = None  # infected source point
        # self.infected_location = None  # infected location

        self.infection_variant = kwargs.get('disease_variant', None)
        # TODO ADD SAVE LOAD FEATURE FOR FOLLOWING
        self.infection_history = []
        self.disease_state_set_time = kwargs.get('disease_state_set_time', -1)
        self.is_monthly_weekend = False  # add to description TODO set initialize parameters

        # no save load needed for following
        self.is_day_finished = False
        self.route = []  # route that point is going to take. (list of location refs)
        self.current_target_idx = -1  # current location in the route (index of the route list)
        self.current_loc_enter = -1
        self.current_loc_leave = -1
        self.is_transporter = 0

        self.roster_days = []  # [i for i in range(7) if np.random.rand() < Person.roster_ratio]
        self.is_roster_day = True

        self.current_loc = None
        self.current_trans = None

        self.latched_to = None
        self.latch_onto_hash = None

        self.update_temp(0.0)
        Person.all_people.append(self)

    def __repr__(self):
        return self.class_name + "-" + str(self.ID)

    def __str__(self):
        return str(self.ID)

    def print(self):
        d = self.get_description_dict()
        for key in d.keys():
            print(key, d[key])
        d = self.get_fine_description_dict(Time.get_time())
        for key in d.keys():
            print(key, d[key])

    @staticmethod
    def get_person(_id):
        return Person.all_people[int(_id)]

    def get_description_dict(self):

        from backend.python.location.Location import Location
        inf_loc = int(self.features[self.ID, PF_infected_loc_id])
        inf_source = int(self.features[self.ID, PF_infected_source_id])
        d = {'person': self.ID,
             'person_class': ClassNameMaps.pc_map[self.class_name],
             'gender': self.features[self.ID, PF_gender],
             'age': self.features[self.ID, PF_age],
             'base_immunity': self.features[self.ID, PF_base_immunity],
             'immunity_boost': self.features[self.ID, PF_immunity_boost],
             # 'behaviour': self.features[self.ID, PF_behaviour],
             'happiness': self.features[self.ID, PF_happiness],
             'base_happiness': self.features[self.ID, PF_base_happiness],
             'social_class': self.features[self.ID, PF_social_class],
             'daily_income': self.features[self.ID, PF_daily_income],
             'economic_status': self.features[self.ID, PF_economic_status],
             'character_vector': self.character_vector,

             'route': ' '.join(
                 map(str, RoutePlanningEngine.convert_route_to_occupancy_array(self.route, ClassNameMaps.lc_map, 5))),
             'route_len': len(self.route),

             'state': int(self.features[self.ID, PF_state]),
             'disease_state': int(self.features[self.ID, PF_disease_state]),
             'disease_variant': "" if self.infection_variant is None or str(
                 self.infection_variant) == "nan" else self.infection_variant.name,
             'disease_state_set_time': self.disease_state_set_time,
             'is_asymptotic': int(self.features[self.ID, PF_is_asymptotic]) if self.is_infected() else -1,
             'asymptotic_chance': self.features[self.ID, PF_asymptotic_chance],
             'hygiene_p': self.features[self.ID, PF_hygiene_p],
             'tested_positive_time': self.features[self.ID, PF_tested_positive_time],
             'last_tested_time': self.features[self.ID, PF_last_tested_time],
             'temp': self.features[self.ID, PF_temp],

             'infected_time': self.features[self.ID, PF_infected_time],
             'infected_source_class': ClassNameMaps.pc_map[
                 Person.get_person(inf_source).class_name] if inf_source != -1 else -1,
             'infected_source_id': inf_source,
             'infected_loc_class': ClassNameMaps.lc_map[
                 Location.get_location(inf_loc).class_name] if inf_loc != -1 else -1,
             'infected_loc_id': inf_loc,

             'home_loc': self.home_loc.ID,
             'home_weekend_loc': self.home_weekend_loc.ID if self.home_weekend_loc is not None else -1,
             'work_loc': self.work_loc.ID if self.work_loc is not None else -1,
             'main_trans': ClassNameMaps.mc_map[self.main_trans.class_name] if self.main_trans is not None else -1,
             }

        return d

    def get_fine_description_dict(self, mins):
        d = {
            'person': self.ID,
            'person_class': ClassNameMaps.pc_map[self.class_name],  # redundant
            'current_location_id': int(
                self.get_current_location().ID) if self.get_current_location() is not None else -1,
            'current_location_class': ClassNameMaps.lc_map[self.get_current_location().class_name],
            'current_movement_id': int(self.current_trans.ID) if self.current_trans is not None else -1,
            'current_movement_class': ClassNameMaps.mc_map[
                self.current_trans.class_name] if self.current_trans is not None else -1,
            'cur_tar_idx': len(self.route) - 1 if self.is_day_finished else self.current_target_idx,
            'route_len': len(self.route),
            'time': mins,
            'is_day_finished': int(self.is_day_finished),

            'current_loc_enter': self.current_loc_enter,
            'current_loc_leave': int(self.current_loc_leave * 100) / 100,
            'destination': self.all_destinations[self.ID],

            'x': int(self.features[self.ID, PF_px] * 100) / 100,
            'y': int(self.features[self.ID, PF_py] * 100) / 100,

            'vx': int(self.features[self.ID, PF_vx] * 100) / 100,
            'vy': int(self.features[self.ID, PF_vx] * 100) / 100,

        }
        return d

    def initialize_age(self, min_age, max_age):
        return np.random.randint(int(min_age), int(max_age))

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
            # Logger.log(
            #     f"{self.ID} {self.class_name} not at home when day resets. (Now at {self.get_current_location().name} "
            #     f"from {Time.i_to_time(self.all_movement_enter_times[self.ID])} next target {self.get_next_target().loc.name}) "
            #     f"CTarget {self.current_target_idx}/{len(self.route) - 1} "
            #     , 'c')
            ret = False

        # removing all latched people from transporters because we can't have them
        # inside a transporter when resetting the day
        if isinstance(self, Transporter):
            self.force_delatch_and_teleport_all()

        self.is_day_finished = False
        self.current_target_idx = 0
        self.is_roster_day = t // Time.DAY // 7 in self.roster_days

        from backend.python.RoutePlanningEngine import RoutePlanningEngine
        from backend.python.CovEngine import CovEngine

        RoutePlanningEngine.set_route(self, t)
        # self.adjust_leaving_time(t)
        self.character_vector = np.dot(self.get_character_transform_matrix(), self.character_vector.T)
        self.features[self.ID, PF_immunity_boost] *= CovEngine.daily_immunity_boost_dec_factor
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
        # msg = f"{self.ID} incremented target from {self.get_current_target()} to "
        if self.current_target_idx + 1 < len(self.route):
            self.current_target_idx = (self.current_target_idx + 1) % len(self.route)
        from backend.python.MovementEngine import MovementEngine
        next_loc = MovementEngine.find_next_location(self)
        # msg += f"{self.get_current_target()} ({self.current_target_idx}/{len(self.route)} target). Next location is {next_loc}."
        # Logger.log(msg, 'i')

    def set_home_loc(self, home_loc):
        self.home_loc = home_loc
        Person.features[self.ID, PF_home_id] = home_loc.ID
        self.route = self.home_loc.get_suggested_sub_route(self, [])
        self.route[0].enter_person(self)

    def set_home_w_loc(self, home_loc):
        self.home_weekend_loc = home_loc
        Person.features[self.ID, PF_home_w_id] = home_loc.ID

    def set_work_loc(self, work):
        self.work_loc = work
        Person.features[self.ID, PF_work_id] = work.ID

    def set_movement(self, movement):
        self.main_trans = movement
        Person.features[self.ID, PF_fm_id] = movement.ID

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

        # if level > 0:
        #     Logger.log(f"{self} is going to {target} that is at level {level}", 'd')
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
            if route[0].loc != self.home_loc and route[0].loc != self.home_weekend_loc and route[
                0].loc != self.work_loc:
                raise Exception(
                    f"Initial location invalid! First location class is {route[0].loc.class_name} for {self.class_name}")
            if route[-1].loc != self.home_loc and route[-1].loc != self.home_weekend_loc and route[
                -1].loc != self.work_loc:
                raise Exception(
                    f"Last location invalid! Last location class is {route[-1].loc.class_name} for {self.class_name}")
        self.route = route
        if move2first:
            self.current_target_idx = 0
            x = route[0].loc.px + np.random.normal(0, 1)
            y = route[0].loc.py + np.random.normal(0, 1)
            self.set_position(x, y, True)
            self.route[0].enter_person(self)

    def set_position(self, new_x, new_y, force=False):
        if not self.latched_to or force:
            self.features[self.ID, PF_px] = new_x
            self.features[self.ID, PF_py] = new_y
        else:
            start = self.all_movement_enter_times[self.ID]
            print(self.get_description_dict())
            raise Exception(f"Tried to move {self.ID} in {self.get_current_location()} (enter at:{start})."
                            f"Going to {self.get_next_target()}")

    def set_velocity(self, new_vx, new_vy):
        self.features[self.ID, PF_vx] = new_vx
        self.features[self.ID, PF_vy] = new_vy

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
        if len(self.route) == 0:
            return Target(self.home_loc, -1, None)
        return self.route[min(self.current_target_idx + 1, len(self.route) - 1)]

    def get_effective_immunity(self):
        return min(1, max(0, self.features[self.ID, PF_base_immunity] +
                          self.features[self.ID, PF_immunity_boost] * (
                                  1 - self.features[self.ID, PF_base_immunity])))

    def set_infected(self, t, p, loc, common_p, variant_name=None):
        self.features[self.ID, PF_state] = State_INFECTED
        self.features[self.ID, PF_infected_time] = t
        self.features[self.ID, PF_infected_source_id] = p.ID
        self.features[self.ID, PF_infected_loc_id] = loc.ID
        self.features[self.ID, PF_is_asymptotic] = int(np.random.rand() < self.features[self.ID, PF_asymptotic_chance])
        self.infection_variant = CovEngine.get_infect_variant(self, source=p, name=variant_name)

        # print(self, p, variant_name, type(variant_name), self.infection_variant)

        self.set_disease_state(DiseaseState_INCUBATION, t)
        # self.source = p
        # self.infected_location = loc
        self.update_temp(common_p)

    def record_infection_history(self):
        # TODO save load infection history
        self.infection_history.append({
            "infected_time": self.features[self.ID, PF_infected_time],
            "infection_end_time": Time.get_time(),
            "infected_source_id": self.features[self.ID, PF_infected_source_id],
            "infected_loc_id": self.features[self.ID, PF_infected_loc_id],
            "is_asymptotic": self.features[self.ID, PF_is_asymptotic],
            "recovered_from_state": self.features[self.ID, PF_disease_state]
        })

    def set_recovered(self):
        self.record_infection_history()
        self.features[self.ID, PF_state] = State_RECOVERED  # TODO RECOVERED OR SUSCEPTIBLE
        self.features[self.ID, PF_disease_state] = DiseaseState_INCUBATION

    def set_susceptible(self):
        self.features[self.ID, PF_state] = State_SUSCEPTIBLE

    def set_dead(self):
        self.record_infection_history()
        self.features[self.ID, PF_state] = State_DEAD
        self.features[self.ID, PF_temp] = 25
        self.features[self.ID, PF_vx] = 0
        self.features[self.ID, PF_vy] = 0

    def set_disease_state(self, state, t):
        self.features[self.ID, PF_disease_state] = state
        self.disease_state_set_time = t

    def is_infected(self):
        return self.features[self.ID, PF_state] == State_INFECTED

    def is_recovered(self):
        return self.features[self.ID, PF_state] == State_RECOVERED

    def is_dead(self):
        return self.features[self.ID, PF_state] == State_DEAD

    def is_susceptible(self):
        return self.features[self.ID, PF_state] == State_SUSCEPTIBLE

    def is_tested_positive(self):
        return self.features[self.ID, PF_tested_positive_time] > 0

    def update_temp(self, common_p):
        if self.is_infected():
            self.features[self.ID, PF_temp] = np.random.normal(*Person.infect_temperature)
        elif self.is_recovered() or self.is_susceptible():
            if np.random.rand() < common_p:  # Common fever
                self.features[self.ID, PF_temp] = np.random.normal(*Person.infect_temperature)
            else:
                self.features[self.ID, PF_temp] = np.random.normal(*Person.normal_temperature)
        elif self.is_dead():
            self.features[self.ID, PF_temp] = 25
