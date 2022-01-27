from backend.python.location.Location import Location
from backend.python.transport.Walk import Walk


class Cemetery(Location):
    def get_suggested_sub_route(self, point, route_so_far):
        return route_so_far

    def __init__(self, shape, x, y, name,
                 **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.set_quarantined(False, 0)
        self.override_transport = Walk()

    def set_quarantined(self, quarantined, t, recursive=False):
        self.quarantined = False

    def process_people_switching(self, t):
        pass  # no movement when entered. cant go out. therefore we put only dead people here

    def enter_person(self, p):
        if p.is_dead():
            super().enter_person(p)
            p.set_position(self.px, self.py, force=True)
            if p.current_trans is not None:
                p.current_trans.remove_point_from_transport(p)
            if p.latched_to is not None:
                try:
                    p.latched_to.delatch(p, self)  # bus ekedi malaa
                except Exception as e:
                    pass
        else:
            raise Exception(f"Put only dead people! :P {p.__repr__()}")

    def remove_point(self, point):
        raise Exception("Cant remove from cemetery!!!")

    def check_for_leaving(self, t):
        pass
