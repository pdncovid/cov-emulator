from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Mobility

class Transport():
    def __init__(self, velocity_cap: float, mobility_pattern: Mobility):

        self.vcap = velocity_cap
        self.mobility = mobility_pattern


    def move_point(self, location, point):

            if self.mobility == Mobility.RANDOM.value:
                MovementEngine.random_move(location, point, self.vcap, self.vcap)
                # MovementEngine.containment(p)
            elif self.mobility == Mobility.BROWNIAN.value:
                pass

    def transport_point(self,point, destination_xy=None):
        MovementEngine.move_towards(point, destination_xy[0], destination_xy[1])