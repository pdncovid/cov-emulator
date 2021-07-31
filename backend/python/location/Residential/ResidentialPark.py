from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Building import Building
from backend.python.location.Location import Location
import numpy as np


class ResidentialPark(Building):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     if force_dt:
    #         t = route_so_far[-1].leaving_time
    #         _r = [Target(self, t + np.random.randint(0, min(Time.get_duration(1), Time.DAY - t)), None)]
    #
    #     else:
    #         _r = [Target(self, np.random.randint(Time.get_time_from_dattime(17, 0), Time.get_time_from_dattime(18, 30)),
    #                      None)]
    #
    #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
