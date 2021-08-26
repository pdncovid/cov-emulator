from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.functions import get_random_element
from backend.python.location.Location import Location
from backend.python.location.Residential.Home import Home
from backend.python.location.Residential.ResidentialPark import ResidentialPark
from backend.python.location.Stations.BusStation import BusStation
from backend.python.location.Stations.TukTukStation import TukTukStation
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.CommercialZoneBusDriver import CommercialZoneBusDriver
from backend.python.point.SchoolBusDriver import SchoolBusDriver
from backend.python.point.Transporter import Transporter
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Bus import Bus
from backend.python.transport.Walk import Walk


class ResidentialZone(Location):
    # def get_suggested_sub_route(self, point, route_so_far):
    #
    #     homes = self.get_children_of_class(Home)
    #     parks = self.get_children_of_class(ResidentialPark)
    #     home: Location = get_random_element(homes)
    #
    #     route_so_far = super(ResidentialZone, self).get_suggested_sub_route(point, route_so_far)
    #
    #     return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.override_transport = Walk()
        self.spawn_sub_locations(Home, kwargs.get('n_houses', 0), kwargs.get('r_houses', 0), **kwargs)
        self.spawn_sub_locations(ResidentialPark, kwargs.get('n_parks', 0), kwargs.get('r_parks', 0), **kwargs)
        self.spawn_sub_locations(BusStation, 1, kwargs.get('r_parks', 0), **kwargs)
        self.spawn_sub_locations(TukTukStation, 1, kwargs.get('r_parks', 0), **kwargs)
