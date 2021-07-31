from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.Time import Time
from backend.python.location.Commercial.CommercialZone import CommercialZone
from backend.python.location.Education.EducationZone import EducationZone
from backend.python.location.Location import Location
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.ResidentialZone import ResidentialZone
from backend.python.transport.Movement import Movement
from backend.python.transport.Walk import Walk


class RuralBlock(Location):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     raise NotImplementedError()
    #     # while route_so_far[-1].leaving_time < Time.get_time_from_dattime(20, 0):
    #     #     route_so_far = get_random_element(self.locations).get_suggested_sub_route(point, route_so_far)
    #     # return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.spawn_sub_locations(ResidentialZone, 1, 40,
                                 n_houses=4, r_houses=6, n_parks=1, r_parks=8)
        self.spawn_sub_locations(CommercialZone, 1, 30,
                                 n_buildings=6, r_buildings=5, n_canteens=1, r_canteens=3,
                                 n_areas=10, r_areas=1, area_capacity=5)
        self.spawn_sub_locations(MedicalZone, 1, 30,
                                 n_buildings=1, r_buildings=10,
                                 n_quarantine=1, r_quarantine=2, quarantine_capacity=10)
        self.spawn_sub_locations(EducationZone, 1, 30,
                                 n_buildings=1, r_buildings=10,
                                 n_classrooms=5, r_classrooms=2, classroom_capacity=10,
                                 n_canteens=1, r_canteens=2)
