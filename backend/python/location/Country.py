from backend.python.enums import Mobility, Shape
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport


class Country(Location):
    def __init__(self, ID: int, x: float, y: float, shape: Shape, exitx, exity,
                 name: str):
        super().__init__(ID, x, y, shape, exitx, exity, name)