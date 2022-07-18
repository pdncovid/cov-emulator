import numpy as np

from backend.python.MovementEngine import MovementEngine
from backend.python.Logger import Logger
from backend.python.enums import *

from backend.python.point.Person import Person
from backend.python.transport.Movement import Movement


class Transporter(Person):
    eps = 5  # depend on vehicle size??
    delta = 0.9  # depend on vehicle ??

    def __init__(self, class_info, **kwargs):
        from backend.python.transport.MovementByTransporter import MovementByTransporter
        super().__init__(class_info, **kwargs)
        self.latched_people = []
        self.latched_dst = []
        self.max_latches = kwargs.get('max_latches', class_info['max_passengers'])
        self.is_latchable = True
        self.route_rep = []
        self.route_rep_all_stops = []
        self.is_transporter = 1
        self.set_movement(Movement.all_instances[class_info['main_trans']])

    # override
    def on_enter_location(self, loc, t):
        # if isinstance(point, Transporter):
        if self.home_loc == loc or self.home_weekend_loc == loc:  # don't try to latch. o.w. Latch when resetting!!!
            return
        self.main_trans.try_to_latch_people(loc, self)

    def on_enter_home(self):
        # self.current_trans = self.home_loc.override_transport
        if len(self.latched_people) != 0 and self.current_target_idx == len(self.route) - 1:
            Logger.log(
                f"People ({len(self.latched_people)}) are latched to transporter when the transporter is going home!",
                'c')
            self.force_delatch_and_teleport_all()

    # override
    def set_current_location(self, loc, t):
        super(Transporter, self).set_current_location(loc, t)

        i = 0
        do_check = False
        while i < (len(self.latched_people)):
            loc.enter_person(self.latched_people[i])
            if self.latched_dst[i] == loc:
                self.delatch(i, loc)
                do_check = True
                i -= 1
            i += 1
        if do_check:
            MovementEngine.process_people_switching(self.get_current_location().points, t)

    # override
    def set_position(self, new_x, new_y, force=False):
        dx, dy = new_x - self.features[self.ID, PF_px], new_y - self.features[self.ID, PF_py]
        self.features[self.ID, PF_px] += dx
        self.features[self.ID, PF_py] += dy

        for latched_p in self.latched_people:
            x, y = self.features[latched_p.ID, PF_px], self.features[latched_p.ID, PF_py]
            x += dx + np.random.rand()*2 - 1
            y += dy + np.random.rand()*2 - 1
            latched_p.set_position(x, y, True)

    # override
    def set_infected(self, t, p, loc, common_p, variant_name=None):
        super(Transporter, self).set_infected(t, p, loc, common_p, variant_name)
        self.is_latchable = True  # todo this should be false after tested positive

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
            x, y = Person.features[self.ID, PF_px], Person.features[self.ID, PF_py]
            p.set_position(x + Transporter.delta + abs(np.random.rand() * Transporter.eps),
                           y + + Transporter.delta + abs(np.random.rand() * Transporter.eps), True)
            Logger.log(f"{p.ID} latched to {self.ID}", 'w')
            return True
        else:
            Logger.log(f"Not enough space ({len(self.latched_people)}/{self.max_latches}) to latch onto!", 'd')
            return False

    def delatch_all(self):
        i = 0
        while len(self.latched_people) != 0:
            self.delatch(0, self.get_current_location())

    def force_delatch_and_teleport_all(self):
        if len(self.latched_people) == 0:
            return
        Logger.log(f"Forcefully delatching {len(self.latched_people)} from {self.ID}", 'd')
        while len(self.latched_people) != 0:
            self.delatch(0, self.latched_people[0].route[-1].loc)
        if len(self.latched_people) > 0:
            raise Exception("WHAT?")

    def delatch(self, idx, loc):
        if type(idx) != int:
            idx = self.latched_people.index(idx)
        p = self.latched_people[idx]
        Logger.log(f"{p.ID} will be delatched from  transporter {self.ID} at {self.get_current_location()}", 'd')

        # p.in_inter_trans = False
        p.latched_to = None
        self.latched_people.pop(idx)
        self.latched_dst.pop(idx)

        loc.enter_person(p)
        # get next target and if p cannot goto it using current moving loc
        # transport keep the main trans as the current transport. otherwise people will be stuck in another district.
        from backend.python.MovementEngine import MovementEngine
        if MovementEngine.find_lcp_location(p) != p.get_current_location():  # target is not here. have to go out.
            loc.leave_this_location(p)

            # MovementEngine.find_next_location(p).enter_person(p)

            # trans = p.main_trans
            # trans.add_point_to_transport(p)
        else:
            MovementEngine.find_next_location(p).enter_person(p)

        # last mile problem. Transporter will drop at last closest location. But person has to goto one of the children
        # of the dropped location. Search for locations, and enter to that location.
        # Otherwise person cant go there (SOMETIMES)!.
        # MovementEngine.find_next_location(p).enter_person(p, None)
        # p.get_current_location().add_to_next_location(p)

    # override
    def update_route(self, root, t, new_route_classes=None, replace=False):
        if self.is_tested_positive():
            super(Transporter, self).update_route(root, t, new_route_classes, replace)
        else:
            Logger.log("Not IMPLEMENTED Transporter update route", 'c')
