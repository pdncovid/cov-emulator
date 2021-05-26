from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element, get_time
from backend.python.location.Residential.Home import Home
from backend.python.location.Location import Location
from backend.python.location.Residential.ResidentialPark import ResidentialPark
from backend.python.transport.Walk import Walk


class ResidentialZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):

        homes = self.get_children_of_class(Home)
        parks = self.get_children_of_class(ResidentialPark)
        home: Location = get_random_element(homes)
        _r, _d, _l = [], [], []
        if t < get_time(5, 0):
            _r1, _d1, _l1, t = home.get_suggested_sub_route(point, t, False)
            _r, _d, _l = _r+_r1, _d+_d1, _l+_l1
        elif t < get_time(15, 0):
            _r1, _d1, _l1, t = get_random_element(parks).get_suggested_sub_route(point, t, True)
            _r, _d, _l = _r + _r1, _d + _d1, _l + _l1
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 n_houses=-1, house_r=-1, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)

        if n_houses != -1:
            self.spawn_sub_locations(Home, n_houses, house_r, 0.3, Walk(0.5, Mobility.RANDOM.value))
            self.spawn_sub_locations(ResidentialPark, 1, house_r, 1.0, Walk(0.5, Mobility.RANDOM.value))
