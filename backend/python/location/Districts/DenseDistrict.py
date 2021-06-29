from backend.python.enums import Shape
from backend.python.functions import get_random_element
from backend.python.location.Blocks.RuralBlock import RuralBlock
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Location import Location

class DenseDistrict(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        _r, _d, _l, t = get_random_element(self.locations).get_suggested_sub_route(point, t)
        return _r, _d, _l, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.spawn_sub_locations(UrbanBlock, 15, r=100, infectiousness=0.8, trans=None)
        self.spawn_sub_locations(RuralBlock, 5, r=250, infectiousness=0.4, trans=None)
