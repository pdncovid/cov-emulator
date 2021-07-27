from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.enums import Mobility, Shape
from backend.python.functions import get_random_element
from backend.python.location.Location import Location
from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
from backend.python.location.Medical.Hospital import Hospital
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.Student import Student
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Walk import Walk


class MedicalZone(Location):
    def get_suggested_sub_route(self, point, t, force_dt=False):

        if isinstance(point, CommercialWorker) or isinstance(point, Student):
            hospitals = self.get_children_of_class(Hospital)

            _r, t = get_random_element(hospitals).get_suggested_sub_route(point, t, force_dt)
        elif isinstance(point, BusDriver) or isinstance(point, TuktukDriver):
            _r, t = [Target(self, t + Time.get_duration(.5), None)], t + Time.get_duration(.5)
        else:
            raise NotImplementedError(f"Not implemented for {point.__class__.__name__}")

        return _r, t

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.override_transport = Walk()

        self.spawn_sub_locations(Hospital, kwargs.get('n_buildings', 0), kwargs.get('r_buildings', 0), **kwargs)
        self.spawn_sub_locations(COVIDQuarantineZone, kwargs.get('n_quarantine', 0), kwargs.get('r_quarantine', 0),
                                 capacity=kwargs.get('quarantine_capacity', 0), quarantined=True, **kwargs)
