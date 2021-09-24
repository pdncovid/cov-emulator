from backend.python.enums import Mobility
from backend.python.point.Person import Person
import numpy as np

from backend.python.transport.CommercialZoneBus import CommercialZoneBus


class CommercialWorker(Person):
    combusp = 0.1

    def __init__(self):
        super().__init__()
        # if np.random.random() < CommercialWorker.combusp:
        #     self.main_trans = CommercialZoneBus(Mobility.RANDOM.value)
    def initialize_age(self):
        return np.random.randint(20, 60)
