from backend.python.enums import Mobility
from backend.python.point.Person import Person
import numpy as np

from backend.python.transport.SchoolBus import SchoolBus


class Teacher(Person):
    combusp = 0.1

    def __init__(self):
        super().__init__()

        # if np.random.random() < Student.combusp:
        #     self.main_trans = SchoolBus(Mobility.RANDOM.value)

    def initialize_age(self):
        return np.random.randint(19, 59)
