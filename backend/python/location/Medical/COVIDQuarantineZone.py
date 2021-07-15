from backend.python.Target import Target
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Building import Building
from backend.python.location.Location import Location


class COVIDQuarantineZone(Building):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        _r = [Target(self, t+1, None)]
        # once entered, they will be quarantined

        t = Time.get_current_time(_r, t)
        return _r, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.recovery_p = 0.8

    def set_quarantined(self, quarantined, t, recursive=False):
        self.quarantined = True
