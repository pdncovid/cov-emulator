from backend.python.location.Location import Location
from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.Districts.SparseDistrict import SparseDistrict


class AvgProvince(Location):
    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.spawn_sub_locations(DenseDistrict, 8, 500)
        self.spawn_sub_locations(SparseDistrict, 3, 500)
