from backend.python.location.Room import Room


class Classroom(Room):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     if isinstance(point, Student):
    #
    #         lts = [Time.get_time_from_datetime(10, 30),
    #                Time.get_time_from_datetime(13, 29)]
    #         for lt in lts:
    #             t = route_so_far[-1].leaving_time
    #             if t < lt:
    #                 if force_dt:
    #                     _r = [Target(self, t + np.random.randint(0, (lt - t)), None)]
    #                 else:
    #                     _r = [Target(self, lt, None)]
    #                 break
    #         else:
    #             t = route_so_far[-1].leaving_time
    #             _r = [Target(self, t + min(np.random.randint(0, Time.get_duration(1)), Time.DAY - t), None)]
    #     else:
    #         raise NotImplementedError()
    #
    #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
