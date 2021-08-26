from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.transport.MovementByTransporter import MovementByTransporter


class Tuktuk(MovementByTransporter):
    all_instances = []

    def __init__(self, mobility_pattern=Mobility.RANDOM.value):
        velocity_cap = 20 * 1000 / Time.get_duration(1)
        super().__init__(velocity_cap, mobility_pattern)

        self.destination_reach_eps = 10.0
        self.infectiousness = 1.0
        self.override_level = 3
        Tuktuk.all_instances.append(self)

    def get_in_transport_transmission_p(self):  # todo function of latch density
        return 0.9
