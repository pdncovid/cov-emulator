from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.location.Building import Building
from backend.python.location.Education.Classroom import Classroom
from backend.python.location.Education.SchoolCanteen import SchoolCanteen
from backend.python.location.Location import Location
from backend.python.point.BusDriver import BusDriver
from backend.python.point.SchoolBusDriver import SchoolBusDriver
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Walk import Walk
import numpy as np


class School(Building):
    pb_map = {}

    def get_suggested_sub_route(self, point, t, force_dt=False):
        from backend.python.point.Student import Student
        if isinstance(point, Student):
            classrooms = self.get_children_of_class(Classroom)
            canteens = self.get_children_of_class(SchoolCanteen)
            if point.ID in School.pb_map.keys():
                classroom = School.pb_map[point.ID]
            else:
                classroom = get_random_element(classrooms)
                School.pb_map[point.ID] = classroom

            _r = []
            t_end = np.random.uniform(Time.get_time_from_dattime(13, 30), Time.get_time_from_dattime(14, 30))
            while t < t_end:
                if np.random.rand() < 0.2:
                    _r2, t = get_random_element(canteens).get_suggested_sub_route(point, t, True)
                    _r += _r2

                _r3, t = classroom.get_suggested_sub_route(point, t, force_dt=False)
                _r += _r3
        elif isinstance(point, SchoolBusDriver):
            if t > Time.get_time_from_dattime(8, 30):
                raise Exception(f"school bus driver arriving at the work zone too late ({Time.i_to_time(t)})!!!")
            _r, t = [Target(self, Time.get_time_from_dattime(14, 15), None)], Time.get_time_from_dattime(14, 15)
        elif isinstance(point, BusDriver):
            _r, t = [Target(self, t + Time.get_duration(0.5), None)], t + Time.get_duration(0.5)
        elif isinstance(point, TuktukDriver):
            _r, t = [Target(self, t + Time.get_duration(0.5), None)], t + Time.get_duration(0.5)
        else:
            raise NotImplementedError(point.__repr__())

        return _r, t

    def __init__(self, shape, x, y, name,
                 **kwargs):
        super().__init__(shape, x, y, name, **kwargs)

        self.spawn_sub_locations(Classroom, kwargs.get('n_classrooms', 0), kwargs.get('r_classrooms', 0),
                                 capacity=kwargs.get('classroom_capacity', 0), **kwargs)
        self.spawn_sub_locations(SchoolCanteen, kwargs.get('n_canteens', 0), kwargs.get('r_canteens', 0), **kwargs)
