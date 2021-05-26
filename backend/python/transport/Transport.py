from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Mobility
from backend.python.location.Location import Location


class Transport():
    DEBUG = False

    def __init__(self, velocity_cap: float, mobility_pattern: Mobility):

        self.vcap = velocity_cap
        self.mobility = mobility_pattern

        self.destination_reach_eps = 10.0

        self.infectiousness = 1.0

        self.points = []
        self.points_label = []
        self.points_enter_time = []
        self.points_source = []
        self.points_destination = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__class__.__name__

    def add_point_to_transport(self, point, target_location, t):
        if point.current_trans is not None:
            point.current_trans.remove_point_from_transport(point)
        point.current_trans = self
        self.points.append(point)
        self.points_enter_time.append(t)
        self.points_source.append(point.current_loc)
        self.points_destination.append(target_location)
        self.points_label.append(self.get_point_label(point))

    def update_point_destination(self, point, target_location, t):
        idx = self.points.index(point)
        self.points_enter_time[idx] = t
        self.points_destination[idx] = target_location
        self.points_label[idx] = self.get_point_label(point)

    def remove_point_from_transport(self, point):
        idx = self.points.index(point)
        self.points.pop(idx)
        self.points_enter_time.pop(idx)
        self.points_source.pop(idx)
        self.points_destination.pop(idx)
        self.points_label.pop(idx)

    def get_point_label(self, point):
        raise NotImplementedError()

    def get_in_transport_transmission_p(self):
        raise NotImplementedError()

    def move(self, point, t):
        idx = self.points.index(point)
        destination = self.points_destination[idx]
        if destination is None:
            # move inside location mode
            self.move_point(idx, t)
        else:
            # inter location movement
            self.transport_point(idx, destination.exit, t)

            if MovementEngine.is_close(point, destination.exit, eps=self.destination_reach_eps):
                if point.get_next_location() == destination:
                    destination.enter_person(point, t)
                    if point.current_location + 1 == len(point.route):
                        for _i in range(len(point.route)):
                            if point.leaving_time[_i] != -1:
                                point.leaving_time[_i] += Location._day
                    point.current_location = (point.current_location + 1) % len(point.route)
                else:
                    # even though we add it to the point it should immediately go at next iteration
                    destination.enter_person(point, -10000000000)

    def move_point(self, idx, t):
        point = self.points[idx]
        if self.mobility == Mobility.RANDOM.value:
            MovementEngine.random_move(point.current_loc, point, self.vcap, self.vcap)
            # MovementEngine.containment(p)
        elif self.mobility == Mobility.BROWNIAN.value:
            pass

    def transport_point(self, idx, destination_xy, t):
        point = self.points[idx]
        MovementEngine.move_towards(point, destination_xy[0], destination_xy[1])
