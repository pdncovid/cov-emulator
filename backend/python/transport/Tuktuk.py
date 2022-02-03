from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.transport.MovementByTransporter import MovementByTransporter


class Tuktuk(MovementByTransporter):
    all_instances = []
    pass_through = []

    def __init__(self, mobility_pattern=Mobility.RANDOM.value):
        velocity_cap = 30 * 1000 / Time.get_duration(1)
        super().__init__(velocity_cap, mobility_pattern)
        self.destination_reach_eps = 10.0
        self.override_level = 10
        Tuktuk.all_instances.append(self)

    @staticmethod
    def get_first_instance():
        if len(Tuktuk.all_instances) > 0:
            return Tuktuk.all_instances[0]

    def get_in_transport_transmission_p(self):  # todo function of latch density
        return 0.9
