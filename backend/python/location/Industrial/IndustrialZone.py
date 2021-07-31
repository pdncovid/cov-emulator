import numpy as np

from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.functions import get_random_element
from backend.python.location.Industrial.GarmentBuilding import GarmentBuilding
from backend.python.location.Industrial.GarmentCanteen import GarmentCanteen
from backend.python.location.Industrial.GarmentOffice import GarmentOffice
from backend.python.location.Location import Location
from backend.python.point.BusDriver import BusDriver
from backend.python.point.GarmentAdmin import GarmentAdmin
from backend.python.point.GarmentWorker import GarmentWorker
from backend.python.point.Student import Student
from backend.python.point.TuktukDriver import TuktukDriver


class IndustrialZone(Location):
    pb_map = {}

    def get_suggested_sub_route(self, point, route_so_far):
        if isinstance(point, GarmentWorker):
            canteens = self.get_children_of_class(GarmentCanteen)
            buildings = self.get_children_of_class(GarmentBuilding)
            if point.ID in IndustrialZone.pb_map.keys():
                working_building = IndustrialZone.pb_map[point.ID]
            else:
                working_building = get_random_element(buildings)
                IndustrialZone.pb_map[point.ID] = working_building

            t_end = min(
                np.random.normal(Time.get_time_from_dattime(17, 0), abs(np.random.normal(0, Time.get_duration(1)))),
                Time.get_time_from_dattime(18, 0))
            while route_so_far[-1].leaving_time < t_end:
                route_so_far = working_building.get_suggested_sub_route(point, route_so_far)

                if np.random.rand() < 0.1:
                    route_so_far = get_random_element(canteens).get_suggested_sub_route(point, route_so_far)

        elif isinstance(point, GarmentAdmin):
            canteens = self.get_children_of_class(GarmentCanteen)
            buildings = self.get_children_of_class(GarmentBuilding)
            offices = self.get_children_of_class(GarmentOffice)
            if point.ID in IndustrialZone.pb_map.keys():
                working_office = IndustrialZone.pb_map[point.ID]
            else:
                working_office = get_random_element(offices)
                IndustrialZone.pb_map[point.ID] = working_office
            route_so_far = working_office.get_suggested_sub_route(point, route_so_far)
            t_end = min(
                np.random.normal(Time.get_time_from_dattime(15, 0), abs(np.random.normal(0, Time.get_duration(1)))),
                Time.get_time_from_dattime(18, 0)
            )
            old_loc = working_office
            while route_so_far[-1].leaving_time < t_end:
                if np.random.rand() > 0.3:
                    loc = get_random_element(buildings)
                else:
                    loc = get_random_element(canteens)
                route_so_far = loc.get_suggested_sub_route(point, route_so_far)

                dist = old_loc.get_distance_to(loc)
                old_loc = loc
                route_so_far[-1].leaving_time += dist / point.current_trans.vcap
            route_so_far = working_office.get_suggested_sub_route(point, route_so_far)

        # elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
        #     _r = [Target(self, route_so_far[-1].leaving_timeTime.get_duration(.5), None)]
        #     route_so_far = RoutePlanningEngine.join_routes(route_so_far, _r)
        # elif isinstance(point, Student):
        #     pass
        else:
            route_so_far = super(IndustrialZone, self).get_suggested_sub_route(point, route_so_far)
        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.spawn_sub_locations(GarmentBuilding,
                                 kwargs.get('n_buildings', 0), kwargs.get('r_buildings', 0), **kwargs)
        self.spawn_sub_locations(GarmentCanteen, kwargs.get('n_canteens', 0), kwargs.get('r_canteens', 0), **kwargs)
        self.spawn_sub_locations(GarmentOffice, kwargs.get('n_offices', 0), kwargs.get('r_offices', 0), **kwargs)
