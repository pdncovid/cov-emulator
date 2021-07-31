from backend.python.enums import Mobility
from backend.python.location.Location import Location
from backend.python.transport.Walk import Walk


class Building(Location):
    # def get_suggested_sub_route(self, point, route_so_far) -> (list, int):
    #     raise NotImplementedError()

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.override_transport = Walk(Mobility.RANDOM.value)
