from backend.python.location.Building import Building
from backend.python.location.Education.Classroom import Classroom
from backend.python.location.Education.SchoolCanteen import SchoolCanteen


class School(Building):
    pb_map = {}

    # def get_suggested_sub_route(self, point, route_so_far):
    #     from backend.python.point.Student import Student
    #     if isinstance(point, Student):
    #         classrooms = self.get_children_of_class(Classroom)
    #         canteens = self.get_children_of_class(SchoolCanteen)
    #         if point.ID in School.pb_map.keys():
    #             classroom = School.pb_map[point.ID]
    #         else:
    #             classroom = get_random_element(classrooms)
    #             School.pb_map[point.ID] = classroom
    #
    #         _r = []
    #         t_end = Time.get_random_time_between(route_so_far[-1].leaving_time,13, 30, 14, 30)
    #         while route_so_far[-1].leaving_time < t_end:
    #             if np.random.rand() < 0.2:
    #                 route_so_far = get_random_element(canteens).get_suggested_sub_route(point, route_so_far)
    #
    #             route_so_far = classroom.get_suggested_sub_route(point, route_so_far)
    #
    #     elif isinstance(point, SchoolBusDriver):
    #         # if route_so_far[-1].leaving_time > Time.get_time_from_datetime(9, 30):
    #         #     raise Exception(
    #         #         f"school bus driver arriving at the school too late ({Time.i_to_time(route_so_far[-1].leaving_time)})")
    #         _r = [Target(self, Time.get_random_time_between(route_so_far[-1].leaving_time,14, 30, 15, 0), None)]
    #         route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     elif isinstance(point, Transporter):
    #         _r = [Target(self, route_so_far[-1].leaving_timeTime.get_duration(0.5), None)]
    #         route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     else:
    #         route_so_far = super(School, self).get_suggested_sub_route(point, route_so_far)
    #
    #     return route_so_far

    def __init__(self, shape, x, y, name,
                 **kwargs):
        super().__init__(shape, x, y, name, **kwargs)

        self.spawn_sub_locations(Classroom, kwargs.get('n_classrooms', 0), kwargs.get('r_classrooms', 0),
                                 capacity=kwargs.get('classroom_capacity', 0), **kwargs)
        self.spawn_sub_locations(SchoolCanteen, kwargs.get('n_canteens', 0), kwargs.get('r_canteens', 0), **kwargs)
