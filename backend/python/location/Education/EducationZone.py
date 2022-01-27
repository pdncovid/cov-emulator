from backend.python.functions import get_random_element
from backend.python.location.Education.School import School
from backend.python.location.Location import Location
from backend.python.point.Teacher import Teacher
from backend.python.transport.Walk import Walk


class EducationZone(Location):
    pb_map = {}

    def get_suggested_sub_route(self, point, route_so_far):

        from backend.python.point.Student import Student
        if isinstance(point, Student):

            schools = self.get_children_of_class(School)
            if point.ID in EducationZone.pb_map.keys():
                working_building = EducationZone.pb_map[point.ID]
            else:
                working_building = get_random_element(schools)
                EducationZone.pb_map[point.ID] = working_building

            route_so_far = working_building.get_suggested_sub_route(point, route_so_far)
        elif isinstance(point, Teacher):
            schools = self.get_children_of_class(School)
            if point.ID in EducationZone.pb_map.keys():
                working_building = EducationZone.pb_map[point.ID]
            else:
                working_building = get_random_element(schools)
                EducationZone.pb_map[point.ID] = working_building

            route_so_far = working_building.get_suggested_sub_route(point, route_so_far)
        # elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
        #     route_so_far = [Target(self, route_so_far[-1].leaving_timeTime.get_duration(.5), None)]
        else:
            route_so_far = super(EducationZone, self).get_suggested_sub_route(point, route_so_far)
        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.override_transport = Walk()
        self.spawn_sub_locations(School, kwargs.get('n_buildings', 0), kwargs.get('r_buildings', 0), **kwargs)
