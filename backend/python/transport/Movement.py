from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.enums import Mobility
from backend.python.Time import Time


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Movement(metaclass=Singleton):
    DEBUG = False
    _id = 0
    all_instances = []

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
        Movement.all_instances.append(self)

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

    def add_point_to_transport(self, point, target_location):
        if point.current_trans is not None:
            point.current_trans.remove_point_from_transport(point)
        point.current_trans = self
        self.points.append(point)
        self.points_enter_time.append(Time.get_time())
        self.points_source.append(point.get_current_location())
        self.points_destination.append(target_location)

    def update_point_destination(self, point, target_location):
        idx = self.points.index(point)
        self.points_enter_time[idx] = Time.get_time()
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

    def get_destination_of(self, p):
        idx = self.points.index(p)
        return self.points_destination[idx]

    def move_people(self):
        t = Time.get_time()
        for p in self.points:
            self.move(p, t)

    def move(self, point, t):
        destination = self.get_destination_of(point)
        dt = t - point.current_loc_leave
        if dt > Time.get_duration(1):
            msg = f"OT move {t}-{point.current_loc_leave}={dt} P:{point.ID} in {point.get_current_location().name}(by {self}) "
            msg += f"->{destination}->{point.get_next_target().name} "
            msg += f"(inter_trans {point.in_inter_trans}) "
            msg += " " if destination is None else f"(d={point.x - destination.exit[0]:.2f},{point.y - destination.exit[1]:.2f}) "
            Logger.log(msg, "w")

        if destination is None:
            # move inside location mode
            self.in_location_move(point)
        else:
            # inter location movement
            self.transport_point(point, destination.exit)

            if MovementEngine.is_close(point, destination.exit, eps=self.destination_reach_eps):
                destination.enter_person(point)  # destination point reached
                point.in_inter_trans = False

    def in_location_move(self, point):
        if self.mobility == Mobility.RANDOM.value:
            MovementEngine.random_move(point.get_current_location(), point, self.vcap, self.vcap)
            # MovementEngine.containment(p)
        elif self.mobility == Mobility.BROWNIAN.value:
            pass

    def transport_point(self, point, destination_xy):
        MovementEngine.move_towards(point, destination_xy[0], destination_xy[1], self.vcap, self.vcap)
