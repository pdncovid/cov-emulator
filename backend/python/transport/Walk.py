from backend.python.enums import Mobility
from backend.python.transport.Movement import Movement
import numpy as np


class Walk(Movement):
    def __init__(self, velocity_cap: float, mobility_pattern: Mobility):
        super().__init__(velocity_cap, mobility_pattern)
        self.destination_reach_eps = 1.0

        self.infectiousness = 1.0

    def get_in_transport_transmission_p(self):
        return 1

    def transport_point(self, idx, destination_xy):
        point = self.points[idx]
        point.x += np.sign(destination_xy[0] - point.x) * self.vcap if abs(destination_xy[0] - point.x) > self.vcap else \
        destination_xy[0] - point.x
        point.y += np.sign(destination_xy[1] - point.y) * self.vcap if abs(destination_xy[1] - point.y) > self.vcap else \
        destination_xy[1] - point.y
