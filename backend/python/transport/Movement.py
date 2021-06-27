from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Mobility
from backend.python.functions import get_duration


class Movement:
    DEBUG = False
    _id = 0
    all_transports = []

    def __init__(self, velocity_cap: float, mobility_pattern):
        self.ID = Movement._id
        Movement._id += 1
        self.vcap = velocity_cap
        assert self.vcap >= 1
        self.mobility = mobility_pattern

        self.destination_reach_eps = 10.0

        self.infectious = 1.0

        self.points = []
        self.points_enter_time = []
        self.points_source = []
        self.points_destination = []
        Movement.all_transports.append(self)

    def __repr__(self):
        d = self.get_description_dict()
        return ','.join(map(str, d.values()))

    def __str__(self):
        return self.__class__.__name__ + f"{self.ID}-P:{len(self.points)}"

    def get_description_dict(self):
        d = {'class': self.__class__.__name__, 'id': self.ID, 'vcap': self.vcap,
             "destination_reach_eps": self.destination_reach_eps, "mobility_pattern": self.mobility,
             "infectious": self.infectious}
        return d

    def add_point_to_transport(self, point, target_location, t):
        if point.current_trans is not None:
            point.current_trans.remove_point_from_transport(point)
        point.current_trans = self
        self.points.append(point)
        self.points_enter_time.append(t)
        self.points_source.append(point.get_current_location())
        self.points_destination.append(target_location)

    def update_point_destination(self, point, target_location, t):
        idx = self.points.index(point)
        self.points_enter_time[idx] = t
        self.points_destination[idx] = target_location

    def remove_point_from_transport(self, point):
        idx = self.points.index(point)  # todo point not in points bug
        if self.points[idx].latched_to and self.points[idx].current_trans != self:
            raise Exception("Can't remove latched people from this movement method to another movement method"
                            "Un-latch first, or the behaviour is unexpected!")
        self.points.pop(idx)
        self.points_enter_time.pop(idx)
        self.points_source.pop(idx)
        self.points_destination.pop(idx)

    def get_in_transport_transmission_p(self):
        raise NotImplementedError()

    def move_people(self, t):
        for p in self.points:
            self.move(p, t)

    def move(self, point, t):
        idx = self.points.index(point)
        destination = self.points_destination[idx]
        dt = t - point.current_loc_leave
        if dt > get_duration(1):
            msg = f"OT move {t}-{point.current_loc_leave}={dt} P:{point.ID} in {point.get_current_location().name}(by {self}) "
            msg += f"->{destination}->{point.get_next_target().name} "
            msg += f"(inter_trans {point.in_inter_trans}) "
            msg += " " if destination is None else f"(d={point.x - destination.exit[0]:.2f},{point.y - destination.exit[1]:.2f}) "

            Logger.log(msg, "w")
        if destination is None:
            # move inside location mode
            self.in_location_move(idx, t)
        else:
            # inter location movement
            self.transport_point(idx, destination.exit, t)

            if MovementEngine.is_close(point, destination.exit, eps=self.destination_reach_eps):
                destination.enter_person(point, t)  # destination point reached
                point.in_inter_trans = False

    def in_location_move(self, idx, t):
        point = self.points[idx]
        if self.mobility == Mobility.RANDOM.value:
            MovementEngine.random_move(point.get_current_location(), point, self.vcap, self.vcap)
            # MovementEngine.containment(p)
        elif self.mobility == Mobility.BROWNIAN.value:
            pass

    def transport_point(self, idx, destination_xy, t):
        point = self.points[idx]
        MovementEngine.move_towards(point, destination_xy[0], destination_xy[1], self.vcap, self.vcap)
