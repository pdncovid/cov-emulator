from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.location.Commercial.CommercialWorkArea import CommercialWorkArea
from backend.python.location.Location import Location
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.transport.Transport import Transport
from backend.python.transport.Walk import Walk


class CommercialBuilding(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):
        if isinstance(point, CommercialWorker):

            work_areas = self.get_children_of_class(CommercialWorkArea)
            work_area: Location = get_random_element(work_areas)
            _r1, _d1, _l1, t = work_area.get_suggested_sub_route(point, t, force_dt=True)
            _r2, _d2, _l2, t = get_random_element(work_areas).get_suggested_sub_route(point, t, force_dt=True)
            _r3, _d3, _l3, t = work_area.get_suggested_sub_route(point, t, force_dt=False)

            _r = _r1+_r2+_r3
            _d = _d1+_d2+_d3
            _l = _l1+_l2+_l3
        else:
            raise NotImplementedError()

        return _r, _d, _l, t

    _id_building = 0

    def __init__(self, shape: Shape, x: float, y: float, name: str, exittheta=0.0, exitdist=0.9, infectiousness=1.0,
                 **kwargs):
        super().__init__(shape, x, y, name, exittheta, exitdist, infectiousness, **kwargs)
        CommercialBuilding._id_building += 1

        n_areas = kwargs.get('n_areas')
        area_r = kwargs.get('area_r')
        if n_areas != -1:
            self.spawn_sub_locations(CommercialWorkArea, n_areas, area_r, 0.99, Walk(0.1, Mobility.RANDOM.value))
