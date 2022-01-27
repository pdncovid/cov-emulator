from backend.python.location.Blocks.RuralBlock import RuralBlock
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Location import Location

class DenseDistrict(Location):
    # def get_suggested_sub_route(self, point, route_so_far):
    #     raise NotImplementedError()
    #     # # find the block where point is at
    #     # cur = point.home_loc
    #     # while isinstance(cur, UrbanBlock) or isinstance(cur, RuralBlock):
    #     #     cur = cur.parent_location
    #     # route_so_far = cur.get_suggested_sub_route(point, route_so_far)
    #     # return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
        self.spawn_sub_locations(UrbanBlock, 8, 100)
        self.spawn_sub_locations(RuralBlock, 3, 200)

