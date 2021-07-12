from backend.python.Time import Time
from backend.python.enums import Mobility
from backend.python.transport.MovementGroup import MovementGroup


class Car(MovementGroup):
    def __init__(self, mobility_pattern: Mobility):
        velocity_cap = 40*1000/Time.get_duration(1)
        super().__init__(velocity_cap, mobility_pattern)
        self._vehicle_capacity = 4
        self._vehicle_waiting_time_after_initialization = 1

        self.destination_reach_eps = 2.0

        self.infectiousness = 0.0

