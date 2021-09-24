from backend.python.Logger import Logger

from backend.python.point.Person import Person
import numpy as np


class Transporter(Person):

    def __init__(self):
        super().__init__()
        self.latched_people = []
        self.latched_dst = []
        self.max_latches = 10
        self.is_latchable = True


    # def get_random_route(self, root, t,
    #                      target_classes_or_objs=None,
    #                      possible_override_trans=None,
    #                      ending_time=np.random.randint(Time.get_time_from_datetime(18, 0),
    #                                                    Time.get_time_from_datetime(23, 0))):
    #     if target_classes_or_objs is None:
    #         target_classes_or_objs = []
    #     if possible_override_trans is None:
    #         possible_override_trans = []
    #     arr_locs = []
    #
    #     def dfs(rr):
    #         if rr.override_transport is None:
    #             arr_locs.append(rr)
    #         for tra in possible_override_trans:
    #             if isinstance(rr.override_transport, tra):
    #                 arr_locs.append(rr)
    #                 break
    #         for tar in target_classes_or_objs:
    #             if rr == tar:
    #                 arr_locs.append(rr)
    #             if type(tar) == type:
    #                 if isinstance(rr, tar):
    #                     arr_locs.append(rr)
    #         for child in rr.locations:
    #             dfs(child)
    #
    #     dfs(root)
    #
    #     route, final_time = [], t
    #     old_loc = self.home_loc
    #     _route, final_time = self.get_random_route_through(final_time, [old_loc], False)
    #     route += _route
    #     while True:
    #         loc = get_random_element(get_random_element(arr_locs).locations)  # TODO get from closest to furthest.
    #         if loc == root:  # if we put root to route, people will drop at root. then he/she will get stuck
    #             continue
    #
    #         _route, final_time = self.get_random_route_through(final_time, [loc], force_dt=True)
    #         route += _route
    #         dist = old_loc.get_distance_to(loc)
    #         old_loc = loc
    #         final_time += dist / self.main_trans.vcap
    #
    #         if final_time > ending_time:
    #             break
    #
    #     route = RoutePlanningEngine.add_stops_as_targets_in_route(route, self)
    #     return route

    # override
    def on_enter_location(self, loc, t):
        # if isinstance(point, Transporter):
        self.main_trans.try_to_latch_people(loc)

    # override
    def set_current_location(self, loc, t):
        super(Transporter, self).set_current_location(loc, t)

        i = 0
        do_check = False
        while i < (len(self.latched_people)):
            loc.enter_person(self.latched_people[i])
            if self.latched_dst[i] == loc:
                Logger.log(f"{self.latched_people[i].ID} reached latched destination {self.get_current_location()}"
                           f"from  transporter {self.ID}", 'd')
                self.delatch(i, loc)
                do_check = True
                i -= 1
            i += 1
        if do_check:
            self.get_current_location().check_for_leaving(t)  # added this to re

    # override
    def set_position(self, new_x, new_y, force=False):

        self.all_positions[self.ID] = [new_x, new_y]

        for latched_p in self.latched_people:
            latched_p.set_position(new_x, new_y, True)

    # override
    def set_infected(self, t, p, common_p):
        super(Transporter, self).set_infected(t, p, common_p)
        self.is_latchable = False

    # override
    def set_dead(self):
        Logger.log(f"Transporter {self.ID} is dead. Delatching all latched! This should not happen. If infected and "
                   "critical, reduce working time!", "c")
        self.delatch_all()
        super(Transporter, self).set_dead()

    # override
    def set_recovered(self):
        super(Transporter, self).set_recovered()
        self.is_latchable = True

    # override
    def set_susceptible(self):
        super(Transporter, self).set_susceptible()
        self.is_latchable = True

    # override
    def increment_target_location(self):
        super(Transporter, self).increment_target_location()
        if self.is_day_finished:
            Logger.log(f"Transporter {self.ID} day finished. Delatching all!")
            self.delatch_all()

    def latch(self, p, des):
        if not self.is_latchable:
            return False
        if self.get_current_location() == self.home_loc:
            return False
        if isinstance(p, Transporter):
            Logger.log(f"Cant latch transporter to a transporter", 'd')
            return False
        if p == self:
            raise Exception("Can't latch to self")
        if len(self.latched_people) < self.max_latches:
            self.latched_people.append(p)
            self.latched_dst.append(des)
            p.latched_to = self
            Logger.log(f"{p.ID} latched to {self.ID}", 'w')
            return True
        else:
            Logger.log(f"Not enough space ({len(self.latched_people)}/{self.max_latches}) to latch onto!", 'd')
            return False

    def delatch_all(self):
        i = 0
        while i < (len(self.latched_people)):
            self.delatch(i, self.get_current_location())

    def delatch(self, idx, loc):
        if type(idx) != int:
            idx = self.latched_people.index(idx)
        p = self.latched_people[idx]
        Logger.log(f"{p.ID} will be delatched from  transporter {self.ID} at {self.get_current_location()}",'d')

        # p.in_inter_trans = False
        p.latched_to = None
        self.latched_people.pop(idx)
        self.latched_dst.pop(idx)

        loc.enter_person(p)

        # last mile problem. Transporter will drop at last closest location. But person has to goto one of the children
        # of the dropped location. Search for locations, and enter to that location.
        # Otherwise person cant go there (SOMETIMES)!.
        from backend.python.transport.Walk import Walk
        from backend.python.MovementEngine import MovementEngine
        # MovementEngine.find_next_location(p).enter_person(p, None)
        # p.get_current_location().add_to_next_location(p)



    # override
    def update_route(self, root, t, new_route_classes=None, replace=False):
        if self.is_tested_positive():
            super(Transporter, self).update_route(root, t, new_route_classes, replace)
        else:
            Logger.log("Not IMPLEMENTED Transporter update route", 'c')
