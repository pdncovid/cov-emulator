import numpy as np

from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.location.Room import Room
from backend.python.point.GarmentAdmin import GarmentAdmin


class GarmentOffice(Room):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if isinstance(point, GarmentAdmin):
            lts = [Time.get_time_from_dattime(10, 0),
                   Time.get_time_from_dattime(12, 0),
                   Time.get_time_from_dattime(17, 0)]
            for lt in lts:
                if t < lt:
                    if force_dt:
                        _r = [Target(self, t + np.random.rand()*(lt - t), None)]
                    else:
                        _r = [Target(self, lt, None)]
                    break
            else:
                _r = [Target(self, t + min(np.random.randint(0, Time.get_duration(1)), Time.DAY - t), None)]
        else:
            _r = [Target(self, t + min(np.random.randint(0, Time.get_duration(0.5)), Time.DAY - t), None)]

        t = Time.get_current_time(_r, t)
        return _r, t

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
