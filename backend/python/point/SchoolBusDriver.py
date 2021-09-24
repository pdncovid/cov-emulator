import numpy as np

from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.point.Transporter import Transporter
from backend.python.transport.SchoolBus import SchoolBus


class SchoolBusDriver(Transporter):
    max_latches = 20

    def __init__(self):
        super().__init__()
        self.main_trans = SchoolBus(Mobility.RANDOM.value)

    def initialize_age(self):
        return np.random.randint(25, 45)

    def get_random_route(self, t, end_at):
        route_so_far = super(SchoolBusDriver, self).get_random_route(t, Time.get_random_time_between(t, 5, 0,7, 0))

        # finally visit the working location
        route_so_far = self.get_random_route_through(route_so_far, [self.work_loc], find_from_level=1)
        route_so_far[-1].set_leaving_time(Time.get_random_time_between(t, 13, 30,14, 30))
        # add all the stop in between major route destinations
        route_so_far = RoutePlanningEngine.add_stops_as_targets_in_route(route_so_far, self)

        # come back the same way that bus went in the morning
        route_so_far = RoutePlanningEngine.mirror_route(route_so_far, self, duplicate_last=False, duplicate_first=False)
        return route_so_far

