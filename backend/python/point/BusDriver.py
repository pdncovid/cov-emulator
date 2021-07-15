import numpy as np

from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.functions import get_random_element
from backend.python.point.Transporter import Transporter
from backend.python.transport.Bus import Bus


class BusDriver(Transporter):
    max_latches = 60

    def __init__(self):
        super().__init__()
        self.main_trans = Bus(Mobility.RANDOM.value)

    def set_random_route(self, root, t, target_classes_or_objs=None):
        locs = []

        def dfs(rr):
            if rr.override_transport == Bus or rr.override_transport is None:
                locs.append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(root)
        route, final_time = self.get_suggested_route(t, [self.home_loc], force_dt=False)
        while True:  # first visit around residential zones to collect students

            loc = get_random_element(get_random_element(locs).locations)
            _route, final_time = self.get_suggested_route(final_time, [loc], force_dt=True)
            route += _route
            if final_time > np.random.uniform(Time.get_time_from_dattime(18, 15),
                                              Time.get_time_from_dattime(22, 15)):
                break

        route = RoutePlanningEngine.add_stops_as_targets_in_route(route, self)

        print(f"Bus route for {self.ID} is {list(map(str, route))}")
        self.set_route(route, t)
