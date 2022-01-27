from backend.python.location.Room import Room


class GarmentWorkArea(Room):
    # def get_suggested_sub_route(self, point, route_so_far):
    #
    #     t = route_so_far[-1].leaving_time
    #     if isinstance(point, GarmentWorker):
    #         lts = [Time.get_time_from_datetime(10, 0),
    #                Time.get_time_from_datetime(12, 0),
    #                Time.get_time_from_datetime(17, 0)]
    #         for lt in lts:
    #             if t < lt:
    #                 if force_dt:
    #                     _r = [Target(self, t+np.random.rand() * (lt - t), None)]
    #                 else:
    #                     _r = [Target(self, lt, None)]
    #                 break
    #         else:
    #             _r = [Target(self, t+min(np.random.randint(0, Time.get_duration(1)), Time.DAY - t), None)]
    #     elif isinstance(point, GarmentAdmin):
    #         _r = [Target(self, t+min(np.random.randint(0, Time.get_duration(1)), Time.DAY - t), None)]
    #     else:
    #         raise NotImplementedError()
    #
    #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
