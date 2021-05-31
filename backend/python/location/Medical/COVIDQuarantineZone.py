from backend.python.enums import Mobility, Shape
from backend.python.functions import get_duration, get_time, get_current_time
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport
from backend.python.transport.Walk import Walk
import numpy as np


class COVIDQuarantineZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        _r = [self]
        _d = [1000000000]  # stay indefinitely until recovered
        _l = [-1]

        t = get_current_time(_d, _l, t)
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 capacity=10, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.capacity = capacity

