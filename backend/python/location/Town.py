from backend.python.enums import Mobility, Shape
from backend.python.functions import get_time, get_random_element
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport


class Town(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        _r, _d, _l = [], [], []
        while t < get_time(20, 0):
            _r1, _d1, _l1, t = get_random_element(self.locations).get_suggested_sub_route(point, t)
            _r, _d, _l = _r + _r1, _d + _d1, _l + _l1
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, 0, 0.9, **kwargs)
