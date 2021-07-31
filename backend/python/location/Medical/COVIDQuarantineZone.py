from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Building import Building
from backend.python.location.Location import Location


class COVIDQuarantineZone(Building):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     _r = [Target(self, route_so_far[-1].leaving_time+1, None)]
    #     # once entered, they will be quarantined
    #
    #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     return route_so_far

    def __init__(self, shape, x, y, name,
                 **kwargs):
        super().__init__(shape, x, y, name, **kwargs)

    def set_quarantined(self, quarantined, t, recursive=False):
        self.quarantined = True
