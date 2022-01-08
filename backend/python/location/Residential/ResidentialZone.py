from backend.python.location.GatheringPlace import GatheringPlace
from backend.python.location.Location import Location
from backend.python.location.Residential.Home import Home
from backend.python.location.Residential.ResidentialPark import ResidentialPark
from backend.python.location.Stations.BusStation import BusStation
from backend.python.location.Stations.TukTukStation import TukTukStation
from backend.python.transport.Walk import Walk


class ResidentialZone(Location):
    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.override_transport = Walk()
        self.spawn_sub_locations(Home, kwargs.get('n_houses', 0), kwargs.get('r_houses', 0), **kwargs)
        self.spawn_sub_locations(ResidentialPark, kwargs.get('n_parks', 0), kwargs.get('r_parks', 0), **kwargs)
        self.spawn_sub_locations(BusStation, 1, 1, **kwargs)
        self.spawn_sub_locations(TukTukStation, 1, 1, **kwargs)
        self.spawn_sub_locations(GatheringPlace, 1, kwargs.get('r_parks', 0)/2, **kwargs)
