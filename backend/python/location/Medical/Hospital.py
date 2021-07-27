import numpy as np

from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.enums import Shape
from backend.python.location.Building import Building
from backend.python.location.Location import Location


class Hospital(Building):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if force_dt:
            _r = [Target(self, t + np.random.randint(0, min(Time.get_duration(1), Time.DAY+1 - t)), None)]
        else:
            _r = [Target(self, np.random.randint(Time.get_time_from_dattime(9, 0), Time.DAY), None)]

        t = Time.get_current_time(_r, t)
        return _r, t

    def __init__(self, shape, x, y, name, n_buildings=-1, building_r=-1, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.icu = 10
        self.ward = 100
        self.patients = 1000
        # todo simulate hospital
