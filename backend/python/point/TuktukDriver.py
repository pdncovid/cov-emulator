from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.point.Transporter import Transporter
from backend.python.transport.Tuktuk import Tuktuk
import numpy as np


class TuktukDriver(Transporter):

    def __init__(self):
        super().__init__()
        self.main_trans = Tuktuk(Mobility.RANDOM.value)
        self.max_latches = 3

    def get_random_route(self, t, end_at):
        route_so_far = super(TuktukDriver, self).get_random_route(t, Time.get_random_time_between(t, 5, 0,9, 0))
        ending_time = Time.get_random_time_between(t, 17, 0, 21, 0)
        tries = 0
        while tries < 10:
            # TODO make this part as repeating same bus route
            r_len = len(route_so_far)
            route_so_far = self.get_random_route_at(route_so_far, find_from_level=1)
            if len(route_so_far) == r_len:
                tries += 1

            if route_so_far[-1].leaving_time > ending_time:
                break

        route = RoutePlanningEngine.add_stops_as_targets_in_route(route_so_far, self)
        return route
