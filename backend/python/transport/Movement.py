from backend.python.Time import Time
import pandas as pd

from backend.python.enums import Mobility


# class Singleton(type):
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


class Movement():
    DEBUG = False
    _id = 0
    all_instances = {}
    class_df = pd.read_csv('../python/data/movement_classes.csv').reset_index()

    def __init__(self, class_info, **kwargs):
        self.class_name = class_info['m_class']
        self.ID = Movement._id
        Movement._id += 1

        self.mobility = Mobility.RANDOM.value

        self.vcap = kwargs.get('velocity_cap', class_info['velocity_cap'])*1000/Time.get_duration(1)
        self.destination_reach_eps = kwargs.get('destination_reach_eps', class_info['destination_reach_eps'])
        self.infectiousness = kwargs.get('transport_transmission_p', class_info['transport_transmission_p'])
        self.override_level = kwargs.get('override_level', class_info['override_level'])
        Movement.all_instances[self.class_name] = self
        Movement.all_instances[self.ID] = self

        assert self.vcap >= 1

    def __repr__(self):
        d = self.get_description_dict()
        return ','.join(map(str, d.values()))

    def __str__(self):
        return self.class_name + f"{self.ID}"

    def get_description_dict(self):
        d = {'class': self.class_name, 'id': self.ID, 'vcap': self.vcap,
             "destination_reach_eps": self.destination_reach_eps, "mobility_pattern": self.mobility,
             "infectious": self.infectiousness}
        return d

    # @staticmethod
    # def get_movement(_id):
    #     if _id == -1:
    #         return None
    #     return Movement.all_instances[int(_id)]

    def add_point_to_transport(self, point):
        from backend.python.location.Cemetery import Cemetery
        target_location = point.get_point_destination()
        if isinstance(target_location, Cemetery):
            raise Exception("Cannot put to cemetery like this!!!")
        if point.current_trans != self:
            if point.current_trans is not None:
                point.current_trans.remove_point_from_transport(point)
            point.current_trans = self
            point.all_current_loc_vcap[point.ID] = self.vcap
            point.all_movement_ids[point.ID] = self.ID
            point.all_movement_enter_times[point.ID] = Time.get_time()
            point.all_sources[point.ID] = point.get_current_location().ID

    def remove_point_from_transport(self, point):
        assert point.all_movement_ids[point.ID] == self.ID
        if point.latched_to and point.current_trans != self:
            raise Exception("Can't remove latched people from this movement method to another movement method"
                            "Un-latch first, or the behaviour is unexpected!")
        from backend.python.point.Transporter import Transporter
        from backend.python.transport.MovementByTransporter import MovementByTransporter
        if isinstance(point, Transporter) and isinstance(point.current_trans, MovementByTransporter):
            if len(point.latched_people) != 0:
                raise Exception("Trying to remove transporter from movement without delatching it's transporting people!")
        point.all_movement_ids[point.ID] = -1
        point.all_movement_enter_times[point.ID] = -1
        point.all_sources[point.ID] = -1
        point.all_destinations[point.ID] = -1
        # point.all_destination_exits[point.ID] = point.get_current_location().exit
