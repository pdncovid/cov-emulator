from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.location.Building import Building
from backend.python.location.Location import Location
import numpy as np


class Home(Building):
    def get_suggested_sub_route(self, point, route_so_far):
        if len(route_so_far) == 0:
            # home leaving time in the morning
            from backend.python.point.TuktukDriver import TuktukDriver
            if isinstance(point, TuktukDriver):
                leave_at = np.random.randint(Time.get_time_from_dattime(5, 0), Time.get_time_from_dattime(12, 30))
            else:
                leave_at = np.random.randint(Time.get_time_from_dattime(5, 0), Time.get_time_from_dattime(8, 30))
            _r = [Target(self, leave_at, None)]
            route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        else:
            route_so_far = super(Home, self).get_suggested_sub_route(point, route_so_far)
        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
