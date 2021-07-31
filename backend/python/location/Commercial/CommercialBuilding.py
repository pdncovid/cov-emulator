from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.location.Building import Building
from backend.python.location.Commercial.CommercialWorkArea import CommercialWorkArea
from backend.python.location.Location import Location
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.CommercialZoneBusDriver import CommercialZoneBusDriver
from backend.python.point.TuktukDriver import TuktukDriver


class CommercialBuilding(Building):
    def get_suggested_sub_route(self, point, route_so_far):
        if isinstance(point, CommercialWorker):
            work_areas = self.get_children_of_class(CommercialWorkArea)
            work_area: Location = get_random_element(work_areas)

            route_so_far = work_area.get_suggested_sub_route(point, route_so_far)
            route_so_far = get_random_element(work_areas).get_suggested_sub_route(point, route_so_far)

        # elif isinstance(point, CommercialZoneBusDriver):
        #     _r = [Target(self, Time.get_time_from_dattime(17, 15), None)]
        #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        # elif isinstance(point, BusDriver):
        #     _r = [Target(self, route_so_far[-1].leaving_time + Time.get_duration(0.5), None)]
        #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        # elif isinstance(point, TuktukDriver):
        #     _r = [Target(self, route_so_far[-1].leaving_time + Time.get_duration(0.5), None)]
        #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        else:
            route_so_far = super(CommercialBuilding, self).get_suggested_sub_route(point, route_so_far)

        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)

        self.spawn_sub_locations(CommercialWorkArea, kwargs.get('n_areas', 0), kwargs.get('r_areas', 0),
                                 capacity=kwargs.get('area_capacity', 10), **kwargs)
