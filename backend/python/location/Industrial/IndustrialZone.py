import numpy as np

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

    def get_suggested_sub_route(self, point, t, force_dt=False):
        if isinstance(point, GarmentWorker):
            canteens = self.get_children_of_class(GarmentCanteen)
            buildings = self.get_children_of_class(GarmentBuilding)
            if point.ID in IndustrialZone.pb_map.keys():
                working_building = IndustrialZone.pb_map[point.ID]
            else:
                working_building = get_random_element(buildings)
                IndustrialZone.pb_map[point.ID] = working_building
            _r = []
            t_end = min(
                np.random.normal(Time.get_time_from_dattime(17, 0), abs(np.random.normal(0, Time.get_duration(1)))),
                Time.get_time_from_dattime(18, 0))
            while t < t_end:
                _r1, t = working_building.get_suggested_sub_route(point, t, force_dt)
                _r += _r1
                if np.random.rand() < 0.1:
                    _r2, t = get_random_element(canteens).get_suggested_sub_route(point, t, True)
                    _r += _r2
        elif isinstance(point, GarmentAdmin):
            canteens = self.get_children_of_class(GarmentCanteen)
            buildings = self.get_children_of_class(GarmentBuilding)
            offices = self.get_children_of_class(GarmentOffice)
            if point.ID in IndustrialZone.pb_map.keys():
                working_office = IndustrialZone.pb_map[point.ID]
            else:
                working_office = get_random_element(offices)
                IndustrialZone.pb_map[point.ID] = working_office
            _r, t = working_office.get_suggested_sub_route(point, t, False)
            t_end = min(
                np.random.normal(Time.get_time_from_dattime(15, 0), abs(np.random.normal(0, Time.get_duration(1)))),
                Time.get_time_from_dattime(18, 0)
            )
            old_loc = working_office
            while t < t_end:
                if np.random.rand() > 0.3:
                    loc = get_random_element(buildings)
                else:
                    loc = get_random_element(canteens)
                _r1, t = loc.get_suggested_sub_route(point, t, True)
                _r += _r1

                dist = old_loc.get_distance_to(loc)
                old_loc = loc
                t += dist / point.current_trans.vcap
            _r3, t = working_office.get_suggested_sub_route(point, t, True)
            _r += _r3
        elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
            _r, t = [Target(self, t + Time.get_duration(.5), None)], t + Time.get_duration(.5)
        elif isinstance(point, Student):
            _r, t = [], t
        else:
            raise NotImplementedError(f"Not implemented for {point.__class__.__name__}")
        return _r, t

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.spawn_sub_locations(GarmentBuilding,
                                 kwargs.get('n_buildings', 0), kwargs.get('r_buildings', 0), **kwargs)
        self.spawn_sub_locations(GarmentCanteen, kwargs.get('n_canteens', 0), kwargs.get('r_canteens', 0), **kwargs)
        self.spawn_sub_locations(GarmentOffice, kwargs.get('n_offices', 0), kwargs.get('r_offices', 0), **kwargs)
