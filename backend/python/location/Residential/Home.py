
from backend.python.location.Building import Building

class Home(Building):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     if len(route_so_far) == 0:
    #         # home leaving time in the morning
    #         from backend.python.point.TuktukDriver import TuktukDriver
    #         if isinstance(point, TuktukDriver):
    #             leave_at = Time.get_random_time_between(Time.t + 1, 5,0,12,30)
    #         else:
    #             leave_at =Time.get_random_time_between(Time.t + 1, 5, 0, 12, 0)
    #
    #         _r = [Target(self, leave_at, None)]
    #         route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     else:
    #         route_so_far = super(Home, self).get_suggested_sub_route(point, route_so_far)
    #     return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)

    def enter_person(self, p):
        if p.home_loc == self or p.home_weekend_loc == self:
            p.on_enter_home()
        super(Home, self).enter_person(p)

