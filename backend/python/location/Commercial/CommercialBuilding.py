from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.location.Building import Building
from backend.python.location.Commercial.CommercialWorkArea import CommercialWorkArea
from backend.python.location.Location import Location
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.CommercialZoneBusDriver import CommercialZoneBusDriver
from backend.python.transport.Walk import Walk


class CommercialBuilding(Building):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if isinstance(point, CommercialWorker):
            work_areas = self.get_children_of_class(CommercialWorkArea)
            work_area: Location = get_random_element(work_areas)

            _r1, t = work_area.get_suggested_sub_route(point, t, force_dt=True)
            _r2, t = get_random_element(work_areas).get_suggested_sub_route(point, t, force_dt=True)

            _r = _r1 + _r2
            if not force_dt:
                _r3,  t = work_area.get_suggested_sub_route(point, t, force_dt=False)
                _r += _r3
        elif isinstance(point, CommercialZoneBusDriver):
            _r, t = [Target(self, Time.get_time_from_dattime(17, 15), None)], Time.get_time_from_dattime(17, 15)
        else:
            raise NotImplementedError(point.__repr__())

        return _r, t

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)

        n_areas = kwargs.get('n_areas')
        area_r = kwargs.get('area_r')
        if n_areas != -1:
            self.spawn_sub_locations(CommercialWorkArea, n_areas, area_r, 0.99, Walk(Mobility.RANDOM.value),
                                     capacity=5)
