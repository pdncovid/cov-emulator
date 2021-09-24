from backend.python.point.Person import Person
import numpy as np

class Retired(Person):
    def __init__(self):
        super().__init__()

    def initialize_age(self):
        return np.random.randint(60, 100)
