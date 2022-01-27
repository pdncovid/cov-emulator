from backend.python.functions import get_random_element
from backend.python.location.Location import Location
from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
from backend.python.location.Medical.Hospital import Hospital
from backend.python.point.Transporter import Transporter
from backend.python.transport.Walk import Walk


class MedicalZone(Location):
    def get_suggested_sub_route(self, point, route_so_far):
        if isinstance(point, Transporter):
            route_so_far = super(MedicalZone, self).get_suggested_sub_route(point, route_so_far)
        else:
            hospitals = self.get_children_of_class(Hospital)

            route_so_far = get_random_element(hospitals).get_suggested_sub_route(point, route_so_far)

        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.override_transport = Walk()

        self.spawn_sub_locations(Hospital, kwargs.get('n_buildings', 0), kwargs.get('r_buildings', 0), **kwargs)
        self.spawn_sub_locations(COVIDQuarantineZone, kwargs.get('n_quarantine', 0), kwargs.get('r_quarantine', 0),
                                 capacity=kwargs.get('quarantine_capacity', 0), quarantined=True, **kwargs)
