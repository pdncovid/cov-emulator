from backend.python.enums import Mobility, Shape
from backend.python.location.Location import Location
from backend.python.transport.Walk import Walk


class Cemetery(Location):
    def get_suggested_sub_route(self, point, route_so_far):
        return route_so_far

    def __init__(self, shape, x, y, name,
                 **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.set_quarantined(True, 0)
        self.override_transport = Walk(0.1)

    def set_quarantined(self, quarantined, t, recursive=False):
        self.quarantined = True

    def process_people_switching(self, t):
        pass  # no movement when entered. cant go out. therefore we put only dead people here

    def enter_person(self, p):
        if p.is_dead():
            super().enter_person(p)
            p.set_position(self.x, self.y, force=True)
            if p.current_trans is not None:
                p.current_trans.remove_point_from_transport(p)
            if p.latched_to is not None:
                p.latched_to.delatch(p)  # bus ekedi malaa
        else:
            raise Exception(f"Put only dead people! :P {p.__repr__()}")

    def remove_point(self, point):
        raise Exception("Cant remove from cemetery!!!")

    def check_for_leaving(self, t):
        pass
