import numpy as np

from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Mobility
from backend.python.functions import get_random_element, separate_into_classes
from backend.python.point.Transporter import Transporter
from backend.python.transport.Bus import Bus
from backend.python.transport.CommercialZoneBus import CommercialZoneBus


class CommercialZoneBusDriver(Transporter):
    def __init__(self):
        super().__init__()
        self.max_latches = 10
        self.main_trans = CommercialZoneBus(Mobility.RANDOM.value)

    def set_random_route(self, root, t, target_classes_or_objs=None):
        from backend.python.RoutePlanningEngine import RoutePlanningEngine
        from backend.python.location.Residential.ResidentialZone import ResidentialZone
        locs = separate_into_classes(root)

        target_classes_or_objs = [self.home_loc]
        for i in range(np.random.randint(1, 3)):  # first visit around residential zones to collect workers
            loc = get_random_element(get_random_element(locs[ResidentialZone]).locations)
            target_classes_or_objs += [loc]
        target_classes_or_objs += [self.work_loc]  # finally visit the working location

        route, final_time = self.get_suggested_route(t, target_classes_or_objs)

        # add all the stop in between major route destinations
        route = RoutePlanningEngine.add_stops_as_targets_in_route(route, self)

        # come back the same way that bus went in the morning
        route = RoutePlanningEngine.mirror_route(route, self, duplicate_last=False, duplicate_first=False)

        print(f"Bus route for {self.ID} is {list(map(str, route))}")
        self.set_route(route, t)
