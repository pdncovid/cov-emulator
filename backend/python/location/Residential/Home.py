from backend.python.Target import Target
from backend.python.const import DAY
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Building import Building
from backend.python.location.Location import Location
import numpy as np


class Home(Building):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if force_dt:
            _r = [Target(self, t + np.random.randint(0, min(Time.get_duration(1), DAY - t)),None)]

        else:
            # home leaving time in the morning
            from backend.python.point.TuktukDriver import TuktukDriver
            if isinstance(point, TuktukDriver):
                leave_at = np.random.randint(Time.get_time_from_dattime(5, 0), Time.get_time_from_dattime(12, 30))
            else:
                leave_at = np.random.randint(Time.get_time_from_dattime(5, 0), Time.get_time_from_dattime(8, 30))
            _r = [Target(self, leave_at, None)]
        t = Time.get_current_time(_r, t)
        return _r, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
