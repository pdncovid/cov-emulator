from backend.python.const import DAY
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Location import Location
from backend.python.transport.Movement import Movement
import numpy as np


class CommercialCanteen(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if force_dt:
            _r = [self]
            _d = [np.random.randint(0, min(np.random.normal(Time.get_duration(0.5),Time.get_duration(0.1)), DAY - t))]
            _l = [-1]
        else:
            _r = [self]
            _d = [-1]
            _l = [np.random.randint(Time.get_time_from_dattime(11, 0), Time.get_time_from_dattime(17, 30))]
        t = Time.get_current_time(_d, _l, t)
        return _r, _d, _l, t

    _id_canteen = 0

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        CommercialCanteen._id_canteen += 1
