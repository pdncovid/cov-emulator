import numpy as np

from backend.python.Time import Time
from backend.python.const import DAY
from backend.python.enums import Shape
from backend.python.location.Location import Location


class Hospital(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if force_dt:
            _r = [self]
            _d = [np.random.randint(0, min(Time.get_duration(1), DAY+1 - t))]
            _l = [-1]
        else:
            _r = [self]
            _d = [-1]
            _l = [np.random.randint(Time.get_time_from_dattime(9, 0), DAY)]

        t = Time.get_current_time(_d, _l, t)
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 n_buildings=-1, building_r=-1, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.icu = 10
        self.ward = 100
        self.patients = 1000

