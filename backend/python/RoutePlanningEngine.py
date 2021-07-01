from backend.python.const import DAY
from backend.python.location.Commercial.CommercialZone import CommercialZone
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.Person import Person
import numpy as np


class RoutePlanningEngine:
    @staticmethod
    def get_common_route(point):
        if isinstance(point, CommercialWorker):
            return [CommercialZone]

    @staticmethod
    def get_alternate_route(point):
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

