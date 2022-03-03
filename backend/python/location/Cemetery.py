from backend.python.location.Location import Location
from backend.python.transport.Movement import Movement


class Cemetery(Location):
    def get_suggested_sub_route(self, point, route_so_far):
        return route_so_far

    def __init__(self, x, y, name,**kwargs):
        class_info = Location.class_df.loc[Location.class_df['l_class']=='Cemetery'].iloc[0]
        super().__init__(class_info, x=x, y=y, name=name, **kwargs)
        self.set_quarantined(False, 0)
        self.override_transport = Movement.all_instances['Walk']

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
        if point.is_dead():
            raise Exception("Cant remove from cemetery!!!")
        else:
            print("CHECK THIS!!!!")  # TODO
            super(Cemetery, self).remove_point(point)

    def check_for_leaving(self, t):
        pass
