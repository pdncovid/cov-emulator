from backend.python.Target import Target
from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.Time import Time
from backend.python.location.Residential.Home import Home
from backend.python.location.Location import Location
from backend.python.location.Residential.ResidentialPark import ResidentialPark
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Walk import Walk


class ResidentialZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):

        homes = self.get_children_of_class(Home)
        parks = self.get_children_of_class(ResidentialPark)
        home: Location = get_random_element(homes)
        _r  = []
        if isinstance(point, CommercialWorker):
            if t < Time.get_time_from_dattime(5, 0):
                _r1, t = home.get_suggested_sub_route(point, t, False)
                _r, = _r+_r1
            elif t < Time.get_time_from_dattime(15, 0):
                _r1, t = get_random_element(parks).get_suggested_sub_route(point, t, True)
                _r, = _r + _r1
        elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
            _r, t = [Target(self, -1, 10, None)], t+10
        else:
            raise NotImplementedError(f"Not implemented for {point.__class__.__name__}")
        return _r, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 n_houses=-1, house_r=-1, **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        self.override_transport = Walk(1.5, Mobility.RANDOM.value)

        if n_houses != -1:
            self.spawn_sub_locations(Home, n_houses, house_r, 0.3, Walk(1.5, Mobility.RANDOM.value))
            self.spawn_sub_locations(ResidentialPark, 1, house_r, 1.0, Walk(1.5, Mobility.RANDOM.value))
