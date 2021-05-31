from backend.python.enums import Mobility, Shape
from backend.python.functions import get_duration, get_time, get_current_time
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport
import numpy as np


class CommercialCanteen(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if force_dt:
            _r = [self]
            _d = [np.random.randint(0, min(get_duration(1), Location._day - t))]
            _l = [-1]
        else:
            _r = [self]
            _d = [-1]
            _l = [np.random.randint(get_time(11, 0), get_time(17, 30))]
        t = get_current_time(_d, _l, t)
        return _r, _d, _l, t

    _id_canteen = 0

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        CommercialCanteen._id_canteen += 1
