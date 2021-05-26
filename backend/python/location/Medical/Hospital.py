from backend.python.enums import Mobility, Shape
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport
from backend.python.transport.Walk import Walk


class Hospital(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        pass

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 n_buildings=-1, building_r=-1, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)


