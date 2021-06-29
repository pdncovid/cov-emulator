from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Location import Location


class COVIDQuarantineZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        _r = [self]
        _d = [1]  # doesn't matter because once entered, they will be quarantined
        _l = [-1]

        t = Time.get_current_time(_d, _l, t)
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.recovery_p = 0.8

    def set_quarantined(self, quarantined, t, recursive=False):
        self.quarantined = True


