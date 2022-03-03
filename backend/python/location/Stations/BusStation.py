import numpy as np

from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.Time import Time
from backend.python.location.Cemetery import Cemetery
from itertools import cycle

from backend.python.location.Location import Location


class BusStation(Location):
    # bus_routes = {}
    pass_through = []
    def get_suggested_sub_route(self, point, route_so_far):
        t = route_so_far[-1].leaving_time if len(route_so_far) > 0 else np.random.rand() * Time.get_duration(
            1) + Time.get_time()

        # goto bus station for a little while
        dur = RoutePlanningEngine.get_dur_for_p_in_loc_at_t(route_so_far, point, self, t)
        route_so_far = RoutePlanningEngine.join_routes(route_so_far, [Target(self, t + dur, None)])

        # if the route is defined for the bus, repeat the same route. otherwise define it first

        # from backend.python.point.BusDriver import BusDriver

        from backend.python.transport.Movement import Movement
        bus = Movement.all_instances['Bus']

        if not BusStation.pass_through:
            root = self.get_root()
            # pass_through = ['ResidentialZone', 'IndustrialZone', 'CommercialZone', 'EducationZone', 'MedicalZone']

            # select locations that do not have a override transport or a movement level worse than bus
            loc_wo_trans = root.get_locations_according_function(
                lambda rr: rr.override_transport is None
                           or (rr.override_transport.override_level >= bus.override_level)
                           # and (sum(_r.override_transport is not None for _r in rr.locations) > 0)
            )

            # if the children locations have an override transport, bus will pass through here.
            # If not Bus will goto higher nodes in the tree
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
                if n > 0:  # ==len(r.locations):
                    pass_through.append(r)
            # np.random.shuffle(pass_through)  # todo: shuffle????
            BusStation.pass_through = cycle(pass_through)

            # divide bus routes to separate depth levels
            # pass_through_depths = {}
            # for pass_through_loc in pass_through:
            #     pass_through_depths[pass_through_loc.depth] = []
            # for pass_through_loc in pass_through:
            #     pass_through_depths[pass_through_loc.depth].append(pass_through_loc)

        # if there is no route for the bus, initialize a route.
        # This route will be repeated each time the _work is called.
        if point.class_name == 'BusDriver' and not point.route_rep:
            point.route_rep = []
            loc = next(BusStation.pass_through)
            # pass_through_locs = get_random_element(list(pass_through_depths.values()))  # select bus route depth
            # pass_through_loc = get_random_element(pass_through_locs)    # select particular location
            # loc = point.find_closest(pass_through_loc, self, find_from_level=-1)
            for ch in loc.locations:
                if isinstance(ch, BusStation) or isinstance(ch, Cemetery):
                    continue
                point.route_rep.append(ch)  # pass through all the children
            point.route_rep.append(self.get_root())  # move all to root
            # BusStation.bus_routes[point.ID].append(loc)     # pass through the parent. But teleport once reached

            # drop last item to skip the root from the route? NO. many failed to reach end of route without root
            point.route_rep_all_stops = RoutePlanningEngine.add_all_stops_in_route(point.route_rep)#[:-1]


        bus_route = point.route_rep

        route_so_far = point.get_random_route_through(route_so_far, bus_route, 0)
        route_so_far = point.get_random_route_through(route_so_far, bus_route[::-1], 0)

        return route_so_far

    def __init__(self, class_info, spawn_sub, **kwargs):
        super().__init__(class_info, spawn_sub, **kwargs)
