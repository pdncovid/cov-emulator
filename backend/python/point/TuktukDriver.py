import numpy as np

from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.enums import Mobility
from backend.python.functions import get_random_element
from backend.python.point.Transporter import Transporter
from backend.python.transport.Bus import Bus
from backend.python.transport.Tuktuk import Tuktuk


class TuktukDriver(Transporter):
    def __init__(self):
        super().__init__()
        self.max_latches = 3
        self.main_trans = Tuktuk(np.random.randint(60, 80), Mobility.RANDOM.value)

    def set_random_route(self, root, t, target_classes_or_objs=None):
        arr_locs = []

        def dfs(rr):
            if rr.override_transport == Bus or rr.override_transport is None:
                arr_locs.append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(root)

        target_classes_or_objs = [self.home_loc]
        for i in range(np.random.randint(7, 9)):  # todo find a good way to set up route of the transporters
            loc = get_random_element(get_random_element(arr_locs).locations)
            if loc == root:  # if we put root to bus route, people will drop at root. then he/she will get stuck
                continue
            target_classes_or_objs += [loc]

        route,  final_time = self.get_suggested_route(t, target_classes_or_objs)

        route = RoutePlanningEngine.add_stops_as_targets_in_route(route, self)

        print(f"Tuktuk route for {self.ID} is {list(map(str, route))}")
        self.set_route(route, t)
