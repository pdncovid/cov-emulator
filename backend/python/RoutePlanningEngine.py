import copy

from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.const import DAY
from backend.python.point.Person import Person
import numpy as np


class RoutePlanningEngine:
    @staticmethod
    def get_common_route(point):

        from backend.python.location.Commercial.CommercialZone import CommercialZone
        from backend.python.point.CommercialWorker import CommercialWorker
        if isinstance(point, CommercialWorker):
            return [CommercialZone]

    @staticmethod
    def get_alternate_route(point):
        from backend.python.location.Commercial.CommercialZone import CommercialZone
        from backend.python.location.Medical.MedicalZone import MedicalZone
        if point.temp > point.infect_temperature[0]:
            return [MedicalZone, CommercialZone]
        return RoutePlanningEngine.get_common_route(point)

    @staticmethod
    def update_routes(root, t):
        for p in Person.all_people:
            if (p.is_infected() and p.is_tested_positive()) or p.is_dead():
                # these people cant change route randomly!!!
                continue
            change_change = 0.001
            if t % DAY > 1000:
                change_change *= 0.0001
            if np.random.rand() < change_change:
                p.update_route(root, t % DAY, RoutePlanningEngine.get_alternate_route(p))

    @staticmethod
    def add_stops_as_targets_in_route(route, duration, leaving, p):
        new_route, new_duration, new_leaving = [], [], []
        for i in range(len(route) - 1):
            path = MovementEngine.get_path(route[i], route[i + 1])
            new_route += path[:-1]
            new_duration += [duration[i]] * int(len(path) - 1 > 0) + [1] * max(len(path) - 2, 0)
            new_leaving += [leaving[i]] * int(len(path) - 1 > 0) + [-1] * max(len(path) - 2, 0)
        new_route += [route[-1]]
        new_duration += [duration[-1]]
        new_leaving += [leaving[-1]]
        if new_route[0] != p.home_loc:
            new_route = [route[0]] + new_route
            new_duration = [duration[0]] + new_duration
            new_leaving = [leaving[0]] + new_leaving
        return new_route, new_duration, new_leaving

    @staticmethod
    def mirror_route(route, duration, leaving, p, duplicate_last=False, duplicate_first=False):
        route2, duration2, leaving2 = copy.copy(route), copy.copy(duration), copy.copy(leaving)
        if not duplicate_first:
            route2 = route2[1:]
            duration2 = duration2[1:]
            leaving2 = leaving2[1:]
        if not duplicate_last:
            route2 = route2[:-1]
            duration2 = duration2[:-1]
            leaving2 = leaving2[:-1]
        for i in range(len(leaving2)):
            if leaving2[i] != -1:
                leaving2[i] = -1
                duration2[i] = 1
                Logger.log("Cannot mirror leaving time properly! Falling back to leave after duration of 1 unit time.",
                           'w')
        route = route + route2[::-1]
        duration = duration + duration2[::-1]
        leaving = leaving + leaving2[::-1]
        return route, duration, leaving
