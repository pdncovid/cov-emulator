import numpy as np

from backend.python.Time import Time
from backend.python.functions import get_random_element
from backend.python.location.Commercial.CommercialBuilding import CommercialBuilding
from backend.python.location.Commercial.CommercialCanteen import CommercialCanteen
from backend.python.location.Location import Location
from backend.python.transport.Walk import Walk


class CommercialZone(Location):
    pb_map = {}

    def get_suggested_sub_route(self, point, route_so_far):

        from backend.python.point.CommercialWorker import CommercialWorker
        if isinstance(point, CommercialWorker):
            canteens = self.get_children_of_class(CommercialCanteen)
            buildings = self.get_children_of_class(CommercialBuilding)
            if point.ID in CommercialZone.pb_map.keys():
                working_building = CommercialZone.pb_map[point.ID]
            else:
                working_building = get_random_element(buildings)
                CommercialZone.pb_map[point.ID] = working_building

            t_end = Time.get_random_time_between(route_so_far[-1].leaving_time, 16,0,18,0)
            while route_so_far[-1].leaving_time < t_end:
                route_so_far = working_building.get_suggested_sub_route(point, route_so_far)

                if np.random.rand() < 0.2:
                    route_so_far = get_random_element(canteens).get_suggested_sub_route(point, route_so_far)

        # elif isinstance(point, Student):
        #     _r = [Target(self, route_so_far[-1].leaving_time + Time.get_duration(.25), None)]
        #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        # elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
        #     _r = [Target(self, route_so_far[-1].leaving_time + Time.get_duration(.5), None)]
        #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        else:
            route_so_far = super(CommercialZone, self).get_suggested_sub_route(point, route_so_far)
        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.override_transport = Walk()
        self.spawn_sub_locations(CommercialBuilding,
                                 kwargs.get('n_buildings', 0), kwargs.get('r_buildings', 0), **kwargs)
        self.spawn_sub_locations(CommercialCanteen, kwargs.get('n_canteens', 0), kwargs.get('r_canteens', 0), **kwargs)
