import numpy as np

from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.functions import get_random_element
from backend.python.point.Transporter import Transporter
from backend.python.transport.Bus import Bus


class BusDriver(Transporter):

    def __init__(self):
        super().__init__()
        self.main_trans = Bus(Mobility.RANDOM.value)
        self.max_latches = 60
    def initialize_age(self):
        return np.random.randint(25, 50)

    # def get_random_route(self, t, end_at):
    #     route_so_far = super(BusDriver, self).get_random_route(t, Time.get_random_time_between(t, 5, 0, 9, 0))
    #     ending_time = Time.get_random_time_between(route_so_far[-1].leaving_time,17, 30, 21, 30)
    #     tries = 0
    #     while tries < 10:
    #         # TODO make this part as repeating same bus route
    #         r_len = len(route_so_far)
    #         route_so_far = self.get_random_route_at(route_so_far, find_from_level=1)
    #         if len(route_so_far) == r_len:
    #             tries += 1
    #
    #         if route_so_far[-1].leaving_time > ending_time:
    #             break
    #
    #     route = RoutePlanningEngine.add_stops_as_targets_in_route(route_so_far, self)
    #     return route
