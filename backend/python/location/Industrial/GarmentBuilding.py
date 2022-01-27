from backend.python.location.Building import Building
from backend.python.location.Industrial.GarmentWorkArea import GarmentWorkArea


class GarmentBuilding(Building):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     if isinstance(point, GarmentWorker):
    #         work_areas = self.get_children_of_class(GarmentWorkArea)
    #         route_so_far = get_random_element(work_areas).get_suggested_sub_route(point, route_so_far)
    #         if not force_dt:
    #             route_so_far = get_random_element(work_areas).get_suggested_sub_route(point, route_so_far)
    #
    #     elif isinstance(point, GarmentAdmin):
    #         work_areas = self.get_children_of_class(GarmentWorkArea)
    #         route_so_far = get_random_element(work_areas).get_suggested_sub_route(point, route_so_far)
    #         if not force_dt:
    #             route_so_far = get_random_element(work_areas).get_suggested_sub_route(point, route_so_far)
    #
    #     elif isinstance(point, BusDriver):
    #         _r = [Target(self, route_so_far[-1].leaving_timeTime.get_duration(0.5), None)]
    #         route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     elif isinstance(point, TuktukDriver):
    #         _r = [Target(self, route_so_far[-1].leaving_timeTime.get_duration(0.5), None)]
    #         route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
    #     else:
    #         raise NotImplementedError(point.__repr__())
    #
    #     return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)

        self.spawn_sub_locations(GarmentWorkArea, kwargs.get('n_areas', 0), kwargs.get('r_areas', 0),
                                 capacity=kwargs.get('area_capacity', 10), **kwargs)
