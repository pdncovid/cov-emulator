from backend.python.enums import Mobility
from backend.python.transport.MovementByTransporter import MovementByTransporter


class Bus(MovementByTransporter):
    all_instances = []
    def __init__(self, velocity_cap: float, mobility_pattern: Mobility):
        super().__init__(velocity_cap, mobility_pattern)
        self.destination_reach_eps = 10.0
        self.infectiousness = 1.0
        Bus.all_instances.append(self)


    def get_in_transport_transmission_p(self): # todo function of latch density
        return 0.9


