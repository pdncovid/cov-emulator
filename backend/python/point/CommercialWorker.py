from backend.python.location.Location import Location
from backend.python.point.Person import Person
import numpy as np


class CommercialWorker(Person):

    def __init__(self):
        super().__init__()

    def set_random_route(self, root, t, common_route_classes=None):
        classes = Location.separate_into_classes(root)

        route = []
        duration = []
        leaving = []
        time = t
        for zone in common_route_classes:
            if zone not in classes.keys():
                raise Exception(f"{zone} locations not available in the location tree")
            objs = classes[zone]
            selected = objs[np.random.randint(0, len(objs))]

            _route, _duration, _leaving, time = selected.get_suggested_sub_route(self, time, False)

            route += _route
            duration += _duration
            leaving += _leaving

        self.set_route(route, duration, leaving)
        route[0].enter_person(self, t)
