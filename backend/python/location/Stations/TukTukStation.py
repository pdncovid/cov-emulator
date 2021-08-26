from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.functions import get_random_element
from backend.python.location.Building import Building
from backend.python.location.Location import Location
import numpy as np


class TukTukStation(Building):

    def get_suggested_sub_route(self, point, route_so_far):
        t = route_so_far[-1].leaving_time if len(route_so_far) > 0 else Time.get_time()

        # goto tuktuk station for a little while
        dur = RoutePlanningEngine.get_dur_for_p_in_loc_at_t(point, self, t)
        _r = [Target(self, t + dur, None)]
        route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)

        # There is not defined route for tuk tuks. They will go here and there
        pass_through = ['ResidentialZone', 'IndustrialZone', 'CommercialZone', 'EducationZone', 'MedicalZone']
        np.random.shuffle(pass_through)
        pass_through = pass_through[:np.random.randint(1, len(pass_through))]
        pass_through_objs = []
        for cls in pass_through:
            pass_through_objs.append(point.find_closest(cls, self, find_from_level=-1))

        route_so_far = point.get_random_route_through(route_so_far, pass_through_objs, 1)

        # they come back to station most of the time
        dur = RoutePlanningEngine.get_dur_for_p_in_loc_at_t(point, self, route_so_far[-1].leaving_time)
        _r = [Target(self, route_so_far[-1].leaving_time + dur, None)]
        route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)

        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
