import numpy as np

from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.point.Transporter import Transporter
from backend.python.transport.SchoolBus import SchoolBus


class SchoolBusDriver(Transporter):
    max_latches = 20

    def __init__(self):
        super().__init__()
        self.main_trans = SchoolBus(Mobility.RANDOM.value)

    # def get_random_route(self, root, t,
    #                      target_classes_or_objs=None,
    #                      possible_override_trans=None,
    #                      ending_time=np.random.randint(Time.get_time_from_dattime(18, 0),
    #                                                    Time.get_time_from_dattime(23, 0))):
    #     from backend.python.location.Residential.ResidentialZone import ResidentialZone
    #     from backend.python.RoutePlanningEngine import RoutePlanningEngine
    #     if target_classes_or_objs is None:
    #         target_classes_or_objs = []
    #     if possible_override_trans is None:
    #         possible_override_trans = []
    #     if ResidentialZone not in target_classes_or_objs:
    #         target_classes_or_objs.append(ResidentialZone)
    #
    #     route = super(SchoolBusDriver, self).get_random_route(root, t, target_classes_or_objs,
    #                                                                   possible_override_trans, ending_time)
    #     # finally visit the working location
    #     _route, final_time = self.get_random_route_through(route[-1].leaving_time, [self.work_loc], force_dt=True)
    #     route += _route
    #
    #     # add all the stop in between major route destinations
    #     route = RoutePlanningEngine.add_stops_as_targets_in_route(route, self)
    #
    #     # come back the same way that bus went in the morning
    #     route = RoutePlanningEngine.mirror_route(route, self, duplicate_last=False, duplicate_first=False)
    #     print(f"School Bus route for {self.ID} is {list(map(str, route))}")
    #     return route
