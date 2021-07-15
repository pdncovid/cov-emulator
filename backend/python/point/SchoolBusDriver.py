import numpy as np

from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.functions import get_random_element, separate_into_classes
from backend.python.point.Transporter import Transporter
from backend.python.transport.SchoolBus import SchoolBus


class SchoolBusDriver(Transporter):
    max_latches = 20

    def __init__(self):
        super().__init__()
        self.main_trans = SchoolBus(Mobility.RANDOM.value)

    def set_random_route(self, root, t, target_classes_or_objs=None):
        from backend.python.RoutePlanningEngine import RoutePlanningEngine
        from backend.python.location.Residential.ResidentialZone import ResidentialZone
        locs = separate_into_classes(root)

        route, final_time = self.get_suggested_route(t, [self.home_loc], force_dt=False)
        while True:  # first visit around residential zones to collect students
            loc = get_random_element(get_random_element(locs[ResidentialZone]).locations)
            _route, final_time = self.get_suggested_route(final_time, [loc], force_dt=True)
            route += _route
            if final_time > Time.get_time_from_dattime(8, 15):
                # raise Exception("Commercial zone bus driver arriving at the work zone too late (around 5PM)!!!")
                break
        # finally visit the working location
        _route, final_time = self.get_suggested_route(t, [self.work_loc], force_dt=True)
        route += _route

        # add all the stop in between major route destinations
        route = RoutePlanningEngine.add_stops_as_targets_in_route(route, self)

        # come back the same way that bus went in the morning
        route = RoutePlanningEngine.mirror_route(route, self, duplicate_last=False, duplicate_first=False)

        print(f"School Bus route for {self.ID} is {list(map(str, route))}")
        self.set_route(route, t)
