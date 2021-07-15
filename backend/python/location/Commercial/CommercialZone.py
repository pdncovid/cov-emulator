from backend.python.Target import Target
from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.Time import Time
from backend.python.location.Commercial.CommercialBuilding import CommercialBuilding
from backend.python.location.Commercial.CommercialCanteen import CommercialCanteen
from backend.python.location.Location import Location
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Walk import Walk
import numpy as np


class CommercialZone(Location):
    pb_map = {}

    def get_suggested_sub_route(self, point, t, force_dt=False):

        from backend.python.point.BusDriver import BusDriver
        from backend.python.point.CommercialWorker import CommercialWorker
        from backend.python.point.Student import Student
        if isinstance(point, CommercialWorker):
            canteens = self.get_children_of_class(CommercialCanteen)
            buildings = self.get_children_of_class(CommercialBuilding)
            if point.ID in CommercialZone.pb_map.keys():
                working_building = CommercialZone.pb_map[point.ID]
            else:
                working_building = get_random_element(buildings)
                CommercialZone.pb_map[point.ID] = working_building
            _r = []
            t_end = min(
                np.random.normal(Time.get_time_from_dattime(17, 0), abs(np.random.normal(0, Time.get_duration(1)))),
                Time.get_time_from_dattime(18, 0))
            while t < t_end:
                _r1, t = working_building.get_suggested_sub_route(point, t, force_dt)
                _r += _r1
                if np.random.rand() < 0.2:
                    _r2, t = get_random_element(canteens).get_suggested_sub_route(point, t, True)
                    _r += _r2
        elif isinstance(point, Student):
            _r, t = [Target(self, t + Time.get_duration(.25), None)], t + Time.get_duration(.25)
        elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
            _r, t = [Target(self, t + Time.get_duration(.5), None)], t + Time.get_duration(.5)
        else:
            raise NotImplementedError(f"Not implemented for {point.__class__.__name__}")
        return _r, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 n_buildings=-1, building_r=-1, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)

        if n_buildings != -1:
            self.spawn_sub_locations(CommercialBuilding, n_buildings, building_r, 0.8, Walk(Mobility.RANDOM.value),
                                     n_areas=10, area_r=building_r / 5)
            self.spawn_sub_locations(CommercialCanteen, 2, building_r / 2, 0.95, Walk(Mobility.RANDOM.value))
