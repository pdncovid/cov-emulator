from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.transport.Movement import Movement
import numpy as np


class Walk(Movement):
    all_instances = []

    def __init__(self, mobility_pattern=Mobility.RANDOM.value):
        velocity_cap = 2*1000/Time.get_duration(1)
        super().__init__(velocity_cap, mobility_pattern)
        self.destination_reach_eps = 1.0
        self.infectiousness = 1.0
        self.override_level = 0
        Walk.all_instances.append(self)

    def get_in_transport_transmission_p(self):
        return 1

    # def transport_point(self, point, destination_xy):
    #     point.x += np.sign(destination_xy[0] - point.x) * self.vcap if abs(destination_xy[0] - point.x) > self.vcap else \
    #         destination_xy[0] - point.x
    #     point.y += np.sign(destination_xy[1] - point.y) * self.vcap if abs(destination_xy[1] - point.y) > self.vcap else \
    #         destination_xy[1] - point.y
