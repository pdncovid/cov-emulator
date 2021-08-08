import copy

from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.Target import Target
from backend.python.Time import Time
import numpy as np
import pandas as pd
from backend.python.functions import bs, get_idx_most_likely
import os
import sys


def process_loc_p():
    p = os.getcwd()
    while os.path.basename(p) != 'backend':
        p = os.path.dirname(p)
    p = os.path.join(p, "python")
    p = os.path.join(p, "data")
    p = os.path.join(p, "p_goLocPersonTime.csv")
    return pd.read_csv(p)


class RoutePlanningEngine:
    df_loc_p = process_loc_p()

    @staticmethod
    def get_common_route(point):

        from backend.python.location.Commercial.CommercialZone import CommercialZone
        from backend.python.point.CommercialWorker import CommercialWorker
        if isinstance(point, CommercialWorker):
            return [CommercialZone]

    @staticmethod
    def get_alternate_route(point):
        from backend.python.location.Medical.MedicalZone import MedicalZone
        if point.temp > point.infect_temperature[0]:
            return [MedicalZone]
        return RoutePlanningEngine.get_common_route(point)

    @staticmethod
    def update_routes(root, t):

        from backend.python.point.Person import Person
        for p in Person.all_people:
            if (p.is_infected() and p.is_tested_positive()) or p.is_dead():
                # these people cant change route randomly!!!
                continue
            change_change = 0.001
            if t % Time.DAY > Time.get_time_from_dattime(18, 0):
                change_change *= 0.0001
            if np.random.rand() < change_change:
                p.update_route(root, t % Time.DAY, RoutePlanningEngine.get_alternate_route(p))

    @staticmethod
    def set_route(p, t):
        day = t // Time.DAY
        from backend.python.point.Transporter import Transporter

        move2first = True
        ending_time = Time.get_random_time_between(t, 18, 0, 23, 0)
        # route = p.get_random_route(end_at=ending_time)
        if day % 2 == 0:
            if isinstance(p, Transporter):
                route = p.get_random_route(t, end_at=ending_time)
            else:
                route = p.get_random_route(t, end_at=ending_time)

        else:
            if p.home_weekend_loc is not None:
                # TODO FIX
                route = p.get_random_route(t, end_at=ending_time)
                move2first = False
            else:

                route = p.get_random_route(t, end_at=ending_time)
        route = RoutePlanningEngine.optimize_route(route)
        p.set_route(route, t, move2first)

    @staticmethod
    def optimize_route(route):
        _route = [route[0]]
        for i in range(1, len(route)):
            if _route[-1].is_equal_wo_time(route[i]):
                _route[-1].leaving_time = route[i].leaving_time
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
        route2[0].leaving_time = t
        for i in range(1, len(route2)):
            # t += route2[i - 1].leaving_time - route2[i].leaving_time # todo fix mirror leaving time
            route2[i].leaving_time = t

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
    def get_loc_for_p_at_t(p, t):
        df = RoutePlanningEngine.df_loc_p
        t = str(int(t * (1440 / Time.get_duration(24))))
        lh = df[df['person'] == p.__class__.__name__][[t, 'location']]
        idx = get_idx_most_likely(lh[t])
        if idx == -1:
            return []
        s = lh.iloc[idx, 1]
        if s == '_home':
            return [p.home_loc]
        if s == '_work':
            if p.work_loc is None:
                return []
            return [p.work_loc]
        if s == '_w_home':
            if p.home_weekend_loc is None:
                return []
            return [p.home_weekend_loc]
        return [lh.iloc[idx, 1]]

    @staticmethod
    def get_loc_for_p_at_t2(p, t):

        from backend.python.location.Commercial.CommercialZone import CommercialZone
        from backend.python.location.Education.EducationZone import EducationZone
        from backend.python.location.Industrial.IndustrialZone import IndustrialZone
        from backend.python.location.Residential.ResidentialZone import ResidentialZone
        from backend.python.point.BusDriver import BusDriver
        from backend.python.point.CommercialWorker import CommercialWorker
        from backend.python.point.CommercialZoneBusDriver import CommercialZoneBusDriver
        from backend.python.point.GarmentAdmin import GarmentAdmin
        from backend.python.point.GarmentWorker import GarmentWorker
        from backend.python.point.SchoolBusDriver import SchoolBusDriver
        from backend.python.point.Student import Student
        from backend.python.point.TuktukDriver import TuktukDriver
        loc_at_t = {
            CommercialWorker: {
                Time.get_time_from_dattime(7, 0): 'home',
                Time.get_time_from_dattime(17, 0): 'work',

            },
            GarmentWorker: {
                Time.get_time_from_dattime(7, 0): 'home',
                Time.get_time_from_dattime(17, 0): 'work',

            },
            GarmentAdmin: {
                Time.get_time_from_dattime(9, 0): 'home',
                Time.get_time_from_dattime(17, 0): 'work',

            },
            Student: {
                Time.get_time_from_dattime(7, 0): 'home',
                Time.get_time_from_dattime(14, 0): 'work',

            },
            BusDriver: {
                Time.get_time_from_dattime(5, 0): 'home',
                Time.get_time_from_dattime(6, 0): ResidentialZone,
                Time.get_time_from_dattime(7, 0): CommercialZone,
                Time.get_time_from_dattime(8, 0): EducationZone,
                Time.get_time_from_dattime(9, 0): IndustrialZone,
                Time.get_time_from_dattime(10, 0): CommercialZone,

                Time.get_time_from_dattime(13, 0): IndustrialZone,
                Time.get_time_from_dattime(14, 0): EducationZone,
                Time.get_time_from_dattime(15, 0): IndustrialZone,
                Time.get_time_from_dattime(16, 0): CommercialZone,
            },
            TuktukDriver: {
                Time.get_time_from_dattime(5, 0): 'home',
                Time.get_time_from_dattime(6, 0): ResidentialZone,
                Time.get_time_from_dattime(7, 0): CommercialZone,
                Time.get_time_from_dattime(8, 0): EducationZone,
                Time.get_time_from_dattime(9, 0): IndustrialZone,
                Time.get_time_from_dattime(10, 0): CommercialZone,

                Time.get_time_from_dattime(13, 0): IndustrialZone,
                Time.get_time_from_dattime(14, 0): EducationZone,
                Time.get_time_from_dattime(15, 0): IndustrialZone,
                Time.get_time_from_dattime(16, 0): CommercialZone,
            },
            CommercialZoneBusDriver: {
                Time.get_time_from_dattime(5, 0): 'home',
                Time.get_time_from_dattime(6, 0): ResidentialZone,
                Time.get_time_from_dattime(6, 30): ResidentialZone,
                Time.get_time_from_dattime(7, 0): CommercialZone,

                Time.get_time_from_dattime(17, 0): CommercialZone,
                Time.get_time_from_dattime(17, 15): ResidentialZone,
                Time.get_time_from_dattime(17, 30): ResidentialZone,

            },
            SchoolBusDriver: {
                Time.get_time_from_dattime(5, 0): 'home',
                Time.get_time_from_dattime(6, 0): ResidentialZone,
                Time.get_time_from_dattime(6, 30): ResidentialZone,
                Time.get_time_from_dattime(7, 0): EducationZone,

                Time.get_time_from_dattime(14, 0): EducationZone,
                Time.get_time_from_dattime(14, 15): ResidentialZone,
                Time.get_time_from_dattime(14, 30): ResidentialZone,
            },

        }

        timeline = loc_at_t[p.__class__]
        keys = list(timeline.keys())
        idx = bs(keys, t)
        if idx == len(timeline.keys()):
            return []
        suggestion = timeline[keys[idx]]
        if suggestion == 'home':
            return [p.home_loc]
        if suggestion == 'work':
            return [p.work_loc]
        if type(suggestion) == str:
            raise Exception()
        return [suggestion]

    @staticmethod
    def get_dur_for_p_in_loc_at_t(p, loc, t):
        return Time.get_duration(0.5)
