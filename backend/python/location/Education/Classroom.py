from backend.python.Target import Target
from backend.python.const import DAY
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Room import Room
import numpy as np

from backend.python.point.Student import Student
from backend.python.transport.Walk import Walk


class Classroom(Room):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if isinstance(point, Student):

            lts = [Time.get_time_from_dattime(10, 30),
                   Time.get_time_from_dattime(13, 29)]
            for lt in lts:
                if t < lt:
                    if force_dt:
                        _r = [Target(self, t + np.random.randint(0, (lt - t)), None)]
                    else:
                        _r = [Target(self, lt, None)]
                    break
            else:
                _r = [Target(self, t + min(np.random.randint(0,Time.get_duration(1)), DAY - t),None)]
        else:
            raise NotImplementedError()

        t = Time.get_current_time(_r, t)
        return _r, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
