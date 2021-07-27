from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.functions import get_random_element
from backend.python.location.Location import Location
from backend.python.location.Residential.Home import Home
from backend.python.location.Residential.ResidentialPark import ResidentialPark
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.TuktukDriver import TuktukDriver


class ResidentialZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):

        homes = self.get_children_of_class(Home)
        parks = self.get_children_of_class(ResidentialPark)
        home: Location = get_random_element(homes)
        _r = []
        if isinstance(point, CommercialWorker):
            if t < Time.get_time_from_dattime(5, 0):
                _r1, t = home.get_suggested_sub_route(point, t, False)
                _r, = _r + _r1
            elif t < Time.get_time_from_dattime(15, 0):
                _r1, t = get_random_element(parks).get_suggested_sub_route(point, t, True)
                _r, = _r + _r1
        elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
            _r, t = [Target(self, t + Time.get_duration(.5), None)], t + Time.get_duration(.5)
        else:
            raise NotImplementedError(f"Not implemented for {point.__class__.__name__}")
        return _r, t

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.spawn_sub_locations(Home, kwargs.get('n_houses', 0), kwargs.get('r_houses', 0), **kwargs)
        self.spawn_sub_locations(ResidentialPark, kwargs.get('n_parks', 0), kwargs.get('r_parks', 0), **kwargs)
