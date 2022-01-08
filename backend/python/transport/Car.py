from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.transport.Movement import Movement



class Car(Movement):
    def __init__(self, mobility_pattern=Mobility.RANDOM.value):
        velocity_cap = 40*1000/Time.get_duration(1)
        super().__init__(velocity_cap, mobility_pattern)
        self._vehicle_capacity = 4
        self._vehicle_waiting_time_after_initialization = 1

        self.destination_reach_eps = 2.0

        self.override_level = 2

    def get_in_transport_transmission_p(self):
        return 0
