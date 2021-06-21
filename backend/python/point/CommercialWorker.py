from backend.python.functions import get_random_element
from backend.python.location.Location import Location
from backend.python.point.Person import Person
import numpy as np


class CommercialWorker(Person):
    def __init__(self):
        super().__init__()

    def set_random_route(self, root, t, target_classes_or_objs=None):
        route, duration, leaving, final_time = self.get_suggested_route(t, target_classes_or_objs)
        # route.append(route[-1])
        # duration.append(0)
        # leaving.append(-1)
        self.set_route(route, duration, leaving, t)
