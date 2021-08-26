from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.enums import Shape
from backend.python.Time import Time
from backend.python.functions import get_random_element
from backend.python.location.Building import Building
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Location import Location
import numpy as np


class BusStation(Building):
    bus_routes = {}

    def get_suggested_sub_route(self, point, route_so_far):
        t = route_so_far[-1].leaving_time if len(route_so_far) > 0 else Time.get_time()

        # goto bus station for a little while
        dur = RoutePlanningEngine.get_dur_for_p_in_loc_at_t(point, self, t)
        route_so_far = RoutePlanningEngine.join_routes(route_so_far, [Target(self, t + dur, None)])

        # if the route is defined for the bus, repeat the same route. otherwise define it first

        from backend.python.point.BusDriver import BusDriver
        from backend.python.transport.Bus import Bus
        bus = Bus()
        if point.ID not in BusStation.bus_routes.keys() and isinstance(point, BusDriver):
            BusStation.bus_routes[point.ID] = []
            root = self.get_root()
            # pass_through = ['ResidentialZone', 'IndustrialZone', 'CommercialZone', 'EducationZone', 'MedicalZone']

            loc_wo_trans = root.get_locations_according_function(
                lambda rr: (rr.override_transport is None or
                            rr.override_transport.override_level >= bus.override_level)  # and
                # (sum(_r.override_transport is not None for _r in rr.locations) > 0)
            )
            children_of_wo_trans_locs = set()
            pass_through = []
            for r in loc_wo_trans:
                n = 0
                for loc in r.locations:
                    ort = loc.override_transport
                    if ort is not None and ort.override_level < bus.override_level:
                        n += 1
                    if ort is not None:
                        children_of_wo_trans_locs.add(loc)
                if n > 0:#==len(r.locations):
                    pass_through.append(r)
            np.random.shuffle(pass_through)
            for cls in pass_through:
                loc = point.find_closest(cls, self, find_from_level=-1)
                for ch in loc.locations:
                    if isinstance(ch, BusStation) or isinstance(ch, Cemetery):
                        continue
                    BusStation.bus_routes[point.ID].append(ch)    # pass through all the children
                # BusStation.bus_routes[point.ID].append(loc)     # pass through the parent. But teleport once reached
        bus_route = BusStation.bus_routes[point.ID]

        route_so_far = point.get_random_route_through(route_so_far, bus_route, 1)
        route_so_far = point.get_random_route_through(route_so_far, bus_route[::-1], 1)

        return route_so_far

    def __init__(self, shape, x, y, name, **kwargs):
        super().__init__(shape, x, y, name, **kwargs)
