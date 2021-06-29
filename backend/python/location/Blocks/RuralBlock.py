from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.Time import Time
from backend.python.location.Commercial.CommercialZone import CommercialZone
from backend.python.location.Location import Location
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.ResidentialZone import ResidentialZone
from backend.python.transport.Movement import Movement
from backend.python.transport.Walk import Walk


class RuralBlock(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        _r, _d, _l = [], [], []
        while t < Time.get_time(20, 0):
            _r1, _d1, _l1, t = get_random_element(self.locations).get_suggested_sub_route(point, t)
            _r, _d, _l = _r + _r1, _d + _d1, _l + _l1
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.spawn_sub_locations(ResidentialZone, 1, r=40, infectiousness=0.4, trans=Walk(1.5, Mobility.RANDOM.value),
                                 n_houses=4, house_r=6)
        self.spawn_sub_locations(CommercialZone, 1,  r=30, infectiousness=1.0, trans=Walk(1.5, Mobility.RANDOM.value),
                                 n_buildings=6, building_r=5)
        self.spawn_sub_locations(MedicalZone, 1, r=30, infectiousness=1.0, trans=Walk(1.5, Mobility.RANDOM.value),
                                 n_buildings=2, building_r=10)
