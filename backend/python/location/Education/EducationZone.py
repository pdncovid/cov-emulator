from backend.python.Target import Target
from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.Time import Time
from backend.python.location.Education.School import School
from backend.python.location.Location import Location
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Walk import Walk


class EducationZone(Location):
    pb_map = {}

    def get_suggested_sub_route(self, point, t, force_dt=False):

        from backend.python.point.BusDriver import BusDriver
        from backend.python.point.Student import Student
        if isinstance(point, Student):

            schools = self.get_children_of_class(School)
            if point.ID in EducationZone.pb_map.keys():
                working_building = EducationZone.pb_map[point.ID]
            else:
                working_building = get_random_element(schools)
                EducationZone.pb_map[point.ID] = working_building

            _r, t = working_building.get_suggested_sub_route(point, t, False)

        elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
            _r, t = [Target(self, t + Time.get_duration(.5), None)], t + Time.get_duration(.5)
        else:
            raise NotImplementedError(f"Not implemented for {point.__class__.__name__}")
        return _r, t

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)

        self.spawn_sub_locations(School, kwargs.get('n_buildings', 0), kwargs.get('r_buildings', 0),**kwargs)
