import numpy as np

from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.functions import get_random_element
from backend.python.point.Transporter import Transporter
from backend.python.transport.Bus import Bus
from backend.python.transport.Tuktuk import Tuktuk


class TuktukDriver(Transporter):
    max_latches = 3

    def __init__(self):
        super().__init__()
        self.main_trans = Tuktuk(Mobility.RANDOM.value)

    def set_random_route(self, root, t, target_classes_or_objs=None):
        arr_locs = []

        def dfs(rr):
            if rr.override_transport == Bus or rr.override_transport is None:
                arr_locs.append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(root)
        if target_classes_or_objs is not None:
            Logger.log("Tuktuk driver will ignore target_classes_or_objs when generating routes", 'e')

        route,  final_time = [], t
        old_loc = self.home_loc
        _route,  final_time = self.get_suggested_route(final_time, [old_loc])
        route += _route
        while True:  # todo find a good way to set up route of the transporters
            loc = get_random_element(get_random_element(arr_locs).locations)
            if loc == root:  # if we put root to route, people will drop at root. then he/she will get stuck
                continue

            _route,  final_time = self.get_suggested_route(final_time, [loc])
            route += _route
            dist = old_loc.get_distance_to(loc)
            old_loc = loc
            final_time += dist/self.main_trans.vcap

            if final_time > np.random.randint(Time.get_time_from_dattime(18,0), Time.get_time_from_dattime(23,0)):
                break

        route = RoutePlanningEngine.add_stops_as_targets_in_route(route, self)

        print(f"Tuktuk route for {self.ID} is {list(map(str, route))}")
        self.set_route(route, t)
