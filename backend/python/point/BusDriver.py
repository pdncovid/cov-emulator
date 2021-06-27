import numpy as np

from backend.python.MovementEngine import MovementEngine
from backend.python.functions import get_random_element
from backend.python.point.Transporter import Transporter
from backend.python.transport.Bus import Bus


class BusDriver(Transporter):
    def __init__(self):
        super().__init__()
        self.max_latches = 10

    def set_random_route(self, root, t, target_classes_or_objs=None):
        arr_locs = []

        def dfs(rr):
            if rr.override_transport == Bus or rr.override_transport is None:
                arr_locs.append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(root)

        target_classes_or_objs = [self.home_loc]
        for i in range(np.random.randint(5, 10)):  # todo find a good way to set up route of the transporters
            loc = get_random_element(get_random_element(arr_locs).locations)
            if loc == root:  # if we put root to bus route, people will drop at root. then he/she will get stuck
                continue
            target_classes_or_objs += [loc]

        route, duration, leaving, final_time = self.get_suggested_route(t, target_classes_or_objs)

        # add all the stop in between major route destinations
        new_route, new_duration, new_leaving = [], [], []
        for i in range(len(route) - 1):
            path = MovementEngine.get_path(route[i], route[i + 1])
            new_route += path[:-1]
            new_duration += [duration[i]] * int(len(path) - 1 > 0) + [1] * max(len(path) - 2, 0)
            new_leaving += [leaving[i]] * int(len(path) - 1 > 0) + [-1] * max(len(path) - 2, 0)
        new_route += [route[-1]]
        new_duration += [duration[-1]]
        new_leaving += [leaving[-1]]
        if new_route[0] != self.home_loc:
            new_route = [route[0]] + new_route
            new_duration = [duration[0]] + new_duration
            new_leaving = [leaving[0]] + new_leaving
        # route.append(route[-1])
        # duration.append(0)
        # leaving.append(-1)
        print(f"Bus route for {self.ID} is {list(map(str, new_route))}")
        self.set_route(new_route, new_duration, new_leaving, t)
