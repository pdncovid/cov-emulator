from backend.python.Target import Target
from backend.python.const import DAY
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Location import Location
import numpy as np


class Home(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if force_dt:
            _r = [Target(self, -1,np.random.randint(0, min(Time.get_duration(1), DAY - t)),None)]

        else:
            _r = [Target(self,
                         np.random.randint(Time.get_time_from_dattime(5, 0), Time.get_time_from_dattime(8, 30)),
                         -1, None)]
        t = Time.get_current_time(_r, t)
        return _r, t

    _id_home = 0

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        Home._id_home += 1
