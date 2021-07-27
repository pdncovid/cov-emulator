import numpy as np

from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.location.Building import Building


class GarmentCanteen(Building):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if force_dt:
            _r = [Target(
                self,
                t + np.random.rand()*min(np.random.uniform(Time.get_duration(0.25), Time.get_duration(0.5)), Time.DAY - t),
                None)]
        else:
            _r = [Target(
                self,
                np.random.randint(Time.get_time_from_dattime(11, 0), Time.get_time_from_dattime(17, 30)),
                None)]

        t = Time.get_current_time(_r, t)
        return _r, t

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
