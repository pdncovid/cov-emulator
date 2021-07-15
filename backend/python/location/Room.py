from backend.python.enums import Mobility
from backend.python.location.Location import Location
from backend.python.transport.Walk import Walk


class Room(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False) -> (list, int):
        raise NotImplementedError()

    def __init__(self, shape, x, y, name, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.override_transport = Walk(Mobility.RANDOM.value)