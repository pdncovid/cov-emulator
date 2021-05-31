from backend.python.enums import Mobility, Shape
from backend.python.functions import get_duration, get_random_element, get_time
from backend.python.location.Commercial.CommercialBuilding import CommercialBuilding
from backend.python.location.Commercial.CommercialCanteen import CommercialCanteen
from backend.python.location.Commercial.CommercialWorkArea import CommercialWorkArea
from backend.python.location.Location import Location
from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
from backend.python.location.Medical.Hospital import Hospital
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.transport.Walk import Walk
import numpy as np


class MedicalZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):

        if isinstance(point, CommercialWorker):
            hospitals = self.get_children_of_class(Hospital)

            _r, _d, _l, t = get_random_element(hospitals).get_suggested_sub_route(point, t, force_dt)

        else:
            raise NotImplementedError()

        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 n_buildings=-1, building_r=-1, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)

        if n_buildings != -1:
            self.spawn_sub_locations(Hospital, n_buildings, building_r, 0.8, Walk(0.5, Mobility.RANDOM.value),
                                     n_areas=10, area_r=building_r / 5)
            self.spawn_sub_locations(COVIDQuarantineZone, 1, building_r, 1.0, Walk(0.5, Mobility.RANDOM.value),
                                     capacity=10)
