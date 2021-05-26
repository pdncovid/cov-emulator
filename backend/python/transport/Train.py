from backend.python.enums import Mobility
from backend.python.transport.TransportVehicle import TransportVehicle


class Train(TransportVehicle):
    def __init__(self, velocity_cap: float, mobility_pattern: Mobility):
        super().__init__(velocity_cap, mobility_pattern)
        self._vehicle_capacity = 300
        self._current_label = 0
        self._vehicle_waiting_time_after_initialization = 50

        self.destination_reach_eps = 10.0

        self.infectiousness = 1.0

