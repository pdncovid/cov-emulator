from backend.python.location.Building import Building


class CommercialCanteen(Building):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     if force_dt:
    #         t = route_so_far[-1].leaving_time
    #         _r = [Target(
    #             self,
    #             t + np.random.rand() * min(np.random.uniform(Time.get_duration(0.25), Time.get_duration(0.5)),
    #                                                   Time.DAY - t),
    #             None)]
    #     else:
    #         _r = [Target(
    #             self,
    #             np.random.randint(Time.get_time_from_datetime(11, 0), Time.get_time_from_datetime(17, 30)),
    #             None)]
    #
    #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
