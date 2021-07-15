import copy

from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.Target import Target
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
            return [MedicalZone]
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
    def add_stops_as_targets_in_route(route, p):
        new_route = []
        for i in range(len(route) - 1):
            path = MovementEngine.get_path(route[i].loc, route[i + 1].loc)
            new_route += [Target(path[0], route[i].leaving_time,route[i].likely_trans)]
            new_route += [Target(loc, route[i].leaving_time, None) for loc in path[1:-1]]
        new_route += [route[-1]]
        if new_route[0].loc != p.home_loc:
            new_route = [route[0]] + new_route
        return new_route

    @staticmethod
    def mirror_route(route, p, duplicate_last=False, duplicate_first=False):
        route2 = copy.copy(route)
        if not duplicate_first:
            route2 = route2[1:]
        if not duplicate_last:
            route2 = route2[:-1]
        for i in range(len(route2)):
            if route2[i].leaving_time != -1:
                route2[i].leaving_time = route2[i].leaving_time # todo fix mirror leaving time
                Logger.log("Cannot mirror leaving time properly! Falling back to leave after duration of 1 unit time.",
                           'e')
        route = route + route2[::-1]
        return route
