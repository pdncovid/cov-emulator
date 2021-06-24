from backend.python.enums import Mobility, Shape
from backend.python.functions import get_time, get_random_element
from backend.python.location.Location import Location
from backend.python.transport.Movement import Movement


class Cemetery(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        _r, _d, _l = [], [], []
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.set_quarantined(True, 0)

    def process_people_switching(self, t):
        pass  # no movement when entered. cant go out. therefore we put only dead people here

    def enter_person(self, p, t, target_location=None):
        if p.is_dead():
            super().enter_person(p, t, target_location)
            p.x = self.x
            p.y = self.y
            if p.current_trans is not None:
                p.current_trans.remove_point_from_transport(p)
        else:
            raise Exception("Put only dead people! :P")
