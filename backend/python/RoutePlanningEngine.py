import copy

from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.Target import Target
from backend.python.Time import Time
import numpy as np
import pandas as pd

from backend.python.enums import State, Containment
from backend.python.functions import bs, get_idx_most_likely, get_random_element
import os
import sys


class RoutePlanningEngine:
    df_loc_p = None
    df_loc_o = None
    df_loc_p_1 = None
    df_loc_o_1 = None

    loaded_day_of_week = -1
    loaded_containment = -1

    weekday_shift = 4  # start day of a week is Friday

    # @staticmethod
    # def get_alternate_route(point):
    #     from backend.python.location.Medical.MedicalZone import MedicalZone
    #     if point.temp > point.infect_temperature[0]:
    #         return [MedicalZone]
    #     return []
    #
    # @staticmethod
    # def update_routes(root, t):
    #
    #     from backend.python.point.Person import Person
    #     for p in Person.all_people:
    #         if (p.is_infected() and p.is_tested_positive()) or p.is_dead():
    #             # these people cant change route randomly!!!
    #             continue
    #         change_change = 0.001
    #         if t % Time.DAY > Time.get_time_from_datetime(18, 0):
    #             change_change *= 0.0001
    #         if np.random.rand() < change_change:
    #             p.update_route(root, t % Time.DAY, RoutePlanningEngine.get_alternate_route(p))

    @staticmethod
    def process_loc_p(day_of_week=1, containment=Containment.NONE.value):
        day_of_week = (day_of_week + RoutePlanningEngine.weekday_shift) % 7
        if RoutePlanningEngine.loaded_day_of_week == day_of_week and RoutePlanningEngine.loaded_containment == containment:
            return

        p = os.getcwd()
        while os.path.basename(p) != 'backend':
            p = os.path.dirname(p)
        p = os.path.join(p, "python")
        p = os.path.join(p, "data")
        if 0 <= day_of_week < 3:
            p1 = os.path.join(p, "p_goLocPersonTime.csv")
            p2 = os.path.join(p, "p_goLocPersonTime.csv")
        elif day_of_week == 3:
            p1 = os.path.join(p, "p_goLocPersonTime.csv")
            p2 = os.path.join(p, "p_go_4_LocPersonTime.csv")
        elif day_of_week == 4:
            p1 = os.path.join(p, "p_go_4_LocPersonTime.csv")
            p2 = os.path.join(p, "p_go_5_LocPersonTime.csv")
        elif day_of_week == 5:
            p1 = os.path.join(p, "p_go_5_LocPersonTime.csv")
            p2 = os.path.join(p, "p_go_6_LocPersonTime.csv")
        elif day_of_week == 6:
            p1 = os.path.join(p, "p_go_6_LocPersonTime.csv")
            p2 = os.path.join(p, "p_goLocPersonTime.csv")
        else:
            raise NotImplementedError()

        if containment == Containment.NONE.value:
            pass
        elif containment == Containment.LOCKDOWN.value:
            raise NotImplementedError()
        elif containment == Containment.QUARANTINE.value:
            raise NotImplementedError()
        elif containment == Containment.QUARANTINECENTER.value:
            raise NotImplementedError()
        return p1, p2

    @staticmethod
    def process_loc_o(day_of_week=1, containment=Containment.NONE.value):
        day_of_week = (day_of_week + RoutePlanningEngine.weekday_shift) % 7
        if RoutePlanningEngine.loaded_day_of_week == day_of_week and RoutePlanningEngine.loaded_containment == containment:
            return
        p = os.getcwd()
        while os.path.basename(p) != 'backend':
            p = os.path.dirname(p)
        p = os.path.join(p, "python")
        p = os.path.join(p, "data")

        p1 = os.path.join(p, "p_dtLocPersonTime.csv")
        p2 = os.path.join(p, "p_dtLocPersonTime.csv")

        if containment == Containment.NONE.value:
            pass
        elif containment == Containment.LOCKDOWN.value:
            raise NotImplementedError()
        elif containment == Containment.QUARANTINE.value:
            raise NotImplementedError()
        elif containment == Containment.QUARANTINECENTER.value:
            raise NotImplementedError()
        return p1, p2

    @staticmethod
    def set_parameters(day_of_week, containment):
        p1, p2 = RoutePlanningEngine.process_loc_p(day_of_week, containment)
        o1, o2 = RoutePlanningEngine.process_loc_o(day_of_week, containment)
        if RoutePlanningEngine.df_loc_p_1 is None:
            RoutePlanningEngine.df_loc_p_1 = pd.read_csv(p1)
        if RoutePlanningEngine.df_loc_o_1 is None:
            RoutePlanningEngine.df_loc_o_1 = pd.read_csv(o1)

        RoutePlanningEngine.df_loc_p = RoutePlanningEngine.df_loc_p_1
        RoutePlanningEngine.df_loc_p_1 = pd.read_csv(p2)

        RoutePlanningEngine.df_loc_o = RoutePlanningEngine.df_loc_o_1
        RoutePlanningEngine.df_loc_o_1 = pd.read_csv(o2)

        RoutePlanningEngine.loaded_day_of_week = day_of_week
        RoutePlanningEngine.loaded_containment = containment

    @staticmethod
    def set_route(p, t):

        if p.state == State.DEAD.value:
            return
        from backend.python.point.Transporter import Transporter

        move2first = True
        ending_time = Time.get_random_time_between(t, 21, 0, 22, 0)

        if isinstance(p, Transporter):
            route = p.get_random_route(t, end_at=ending_time)
        else:
            route = p.get_random_route(t, end_at=ending_time)
        if route[-1].loc != p.home_loc and route[-1].loc != p.home_weekend_loc:
            day = t // Time.DAY
            cls_or_obj = RoutePlanningEngine.get_loc_for_p_at_t(route, p,
                                                                (day + 1) * Time.DAY + Time.get_time_from_datetime(1,
                                                                                                                   0))
            target = get_random_element(cls_or_obj)
            route = p.get_random_route_through(route, [target], 1)

        p.set_route(route, t, move2first)

    @staticmethod
    def add_target_to_route(route_so_far, target, enter_t, leave_t):
        start_i, end_i = -1, -1
        for i in range(len(route_so_far)):
            if route_so_far[i].leaving_time > enter_t:
                start_i = i
                break
        if start_i < 0:
            raise Exception()
        for i in range(start_i, len(route_so_far)):
            if route_so_far[i].leaving_time > leave_t:
                end_i = i
                break
        if end_i < start_i:
            raise Exception()
        if start_i == end_i:
            route_so_far.append(target)
            route_so_far.append(route_so_far[-2].__copy__())
            if route_so_far[-1].leaving_time < leave_t:
                route_so_far[-1].set_leaving_time(leave_t)
            route_so_far[start_i].set_leaving_time(enter_t)
        else:
            route_so_far[start_i].set_leaving_time(enter_t)
            route_so_far = route_so_far[:start_i + 1] + route_so_far[end_i:]
            route_so_far.insert(start_i + 1, target)

        return route_so_far

    @staticmethod
    def optimize_route(route):
        _route = [route[0]]
        for i in range(1, len(route)):
            if _route[-1].is_equal_wo_time(route[i]):
                _route[-1].set_leaving_time(route[i].leaving_time)
            else:
                _route.append(route[i])
        return _route

    @staticmethod
    def add_stops_as_targets_in_route(route, p):
        new_route = []
        for i in range(len(route) - 1):
            path = MovementEngine.get_path(route[i].loc, route[i + 1].loc)
            new_route += [Target(path[0], route[i].leaving_time, route[i].likely_trans)]
            new_route += [Target(loc, route[i].leaving_time, None) for loc in path[1:-1]]
        new_route += [route[-1]]
        if new_route[0].loc != p.home_loc:
            new_route = [route[0]] + new_route
        for i in range(len(new_route)-1):
            if new_route[i].leaving_time > new_route[i+1].leaving_time:
                raise Exception()
        return new_route

    @staticmethod
    def mirror_route(route, p, duplicate_last=False, duplicate_first=False):
        route2 = [tar.__copy__() for tar in route]
        if not duplicate_first:
            route2 = route2[1:]
        if not duplicate_last:
            route2 = route2[:-1]
        route2 = route2[::-1]
        t = route[-1].leaving_time
        if len(route2) == 0:
            return route
        route2[0].set_leaving_time(t)
        for i in range(1, len(route2)):
            # t += route2[i - 1].leaving_time - route2[i].leaving_time # todo fix mirror leaving time
            route2[i].set_leaving_time(t)

        route = route + route2
        return route

    @staticmethod
    def join_routes(r1, r2):
        for i in range(len(r1)):
            for j in range(len(r2)):
                if r1[i].leaving_time > r2[j].leaving_time:
                    raise Exception("time conflict when joining routes")
        return r1 + r2

    @staticmethod
    def get_loc_for_p_at_t(route_so_far, p, t):
        day = t // Time.DAY

        if day > Time.get_time() // Time.DAY:
            df_p = RoutePlanningEngine.df_loc_p_1
            df_o = RoutePlanningEngine.df_loc_o_1
        else:
            df_p = RoutePlanningEngine.df_loc_p
            df_o = RoutePlanningEngine.df_loc_o
        t = Time.i_to_minutes(t) % 1440
        t = str(t)
        if len(route_so_far) > 0:
            loc_name = route_so_far[-1].loc.__class__.__name__
            if route_so_far[-1].loc == p.home_loc:
                loc_name = '_home'
            if route_so_far[-1].loc == p.home_weekend_loc:
                loc_name = '_w_home'
            if route_so_far[-1].loc == p.work_loc:
                loc_name = '_work'

            last_t = Time.i_to_minutes(route_so_far[-2].leaving_time) % 1440 if len(route_so_far) > 1 else 0
            dt = str((int(t) - int(last_t)) % 1440)

            p_of_occupancy = df_o[df_o['person'] == p.__class__.__name__][[dt, 'location']]
            p_of_staying = p_of_occupancy.loc[p_of_occupancy['location'] == loc_name][dt].values[0]

            if p_of_staying >= 1 - np.random.exponential(0.1):
                return [route_so_far[-1].loc]

        p_of_visiting = df_p[df_p['person'] == p.__class__.__name__][[t, 'location']]
        idx = get_idx_most_likely(p_of_visiting[t].values, method=0, scale=0.2)
        if idx == -1:
            return [p.home_loc]
        location = p_of_visiting.iloc[idx, 1]
        if location == '_home':
            return [p.home_loc]
        if location == '_work':
            if p.work_loc is None:
                return []
            return [p.work_loc]
        if location == '_w_home':
            if p.home_weekend_loc is None:
                return [p.home_loc]
            return [p.home_weekend_loc]
        return [location]

    @staticmethod
    def get_dur_for_p_in_loc_at_t(p, loc, t):
        from backend.python.point.Transporter import Transporter
        if isinstance(p, Transporter):
            return Time.get_duration(0.1)
        return Time.get_duration(0.5)

    @staticmethod
    def convert_route_to_occupancy_array(route, loc_map, dt):
        arr = []
        t = 0
        for tar in route:
            while t < Time.i_to_minutes(tar.leaving_time) % 1440:
                arr.append(loc_map[tar.loc.__class__.__name__])
                t += dt
        while t < 1440:
            arr.append(loc_map[route[0].loc.__class__.__name__])
            t += dt
        return arr
