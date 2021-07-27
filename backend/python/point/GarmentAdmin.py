from backend.python.point.Person import Person


class GarmentAdmin(Person):
    def __init__(self):
        super().__init__()

    def set_random_route(self, root, t, target_classes_or_objs=None):
        route, final_time = self.get_suggested_route(t, target_classes_or_objs)
        self.set_route(route, t)