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

    # def get_random_route(self, root, t,
    #                      target_classes_or_objs=None,
    #                      possible_override_trans=None,
    #                      ending_time=np.random.randint(Time.get_time_from_dattime(18, 0),
    #                                                    Time.get_time_from_dattime(23, 0))):
    #     if possible_override_trans is None:
    #         possible_override_trans = []
    #     if Bus not in possible_override_trans:
    #         possible_override_trans.append(Bus)
    #     return super(BusDriver, self).get_random_route(root, t,
    #                                                    target_classes_or_objs, possible_override_trans, ending_time)
