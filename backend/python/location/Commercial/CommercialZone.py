from backend.python.enums import Mobility, Shape
from backend.python.functions import get_duration, get_random_element, get_time
from backend.python.location.Commercial.CommercialBuilding import CommercialBuilding
from backend.python.location.Commercial.CommercialCanteen import CommercialCanteen
from backend.python.location.Commercial.CommercialWorkArea import CommercialWorkArea
from backend.python.location.Location import Location
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.transport.Walk import Walk
import numpy as np


class CommercialZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):

        if isinstance(point, CommercialWorker):
            canteens = self.get_children_of_class(CommercialCanteen)
            buildings = self.get_children_of_class(CommercialBuilding)
            working_building: Location = get_random_element(buildings)
            _r, _d, _l = [], [], []
            t_end = min(np.random.normal(get_time(17, 0), abs(np.random.normal(0,get_duration(1)))), get_time(20,0))
            while t < t_end:
                _r1, _d1, _l1, t = working_building.get_suggested_sub_route(point, t, force_dt)
                _r2, _d2, _l2, t = get_random_element(canteens).get_suggested_sub_route(point, t, True)
                _r += _r1 + _r2
                _d += _d1 + _d2
                _l += _l1 + _l2
        else:
            raise NotImplementedError()

        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 n_buildings=-1, building_r=-1, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)

        if n_buildings != -1:
            self.spawn_sub_locations(CommercialBuilding, n_buildings, building_r, 0.8, Walk(0.5, Mobility.RANDOM.value),
                                     n_areas=10, area_r=building_r / 5)
            self.spawn_sub_locations(CommercialCanteen, 2, building_r / 2, 0.95, Walk(0.1, Mobility.RANDOM.value))
