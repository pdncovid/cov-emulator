from backend.python.Target import Target
from backend.python.const import DAY
from backend.python.enums import Mobility, Shape
from backend.python.Time import Time
from backend.python.location.Location import Location
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.transport.Movement import Movement
import numpy as np

from backend.python.transport.Walk import Walk


class CommercialWorkArea(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if isinstance(point, CommercialWorker):

            lts = [Time.get_time_from_dattime(10, 0), Time.get_time_from_dattime(12, 0), Time.get_time_from_dattime(17, 0)]
            for lt in lts:
                if t < lt:
                    if force_dt:
                        _r = [Target(self, -1, np.random.randint(0, (lt - t)), None)]
                    else:
                        _r = [Target(self, lt, -1, None)]
                    break
            else:
                _r = [Target(self, -1, min(np.random.randint(0,Time.get_duration(1)), DAY - t),None)]
        else:
            raise NotImplementedError()

        t = Time.get_current_time(_r, t)
        return _r, t

    _id_area = 0

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.override_transport = Walk(Mobility.RANDOM.value)
        CommercialWorkArea._id_area += 1
