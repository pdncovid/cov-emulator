from backend.python.Logger import Logger
from backend.python.point.Person import Person


class Transporter(Person):

    def set_random_route(self, root, t, target_classes_or_objs=None):
        raise NotImplementedError()

    def __init__(self):
        super().__init__()
        self.latched_people = []
        self.latched_dst = []
        self.max_latches = 10
        self.is_latchable = True

    # override
    def on_enter_location(self, t):
        pass

    # override
    def set_current_location(self, loc, t):
        super(Transporter, self).set_current_location(loc, t)

        for p in self.latched_people:
            loc.enter_person(p, t, target_location=None)
        i = 0
        do_check = False
        while i < (len(self.latched_people)):
            if self.latched_dst[i] == self.latched_people[i].get_current_location():
                Logger.log(f"{self.latched_people[i].ID} reached latched destination {self.get_current_location()}"
                           f"from  transporter {self.ID}")
                self.delatch(i)
                do_check = True
                i -= 1
            i += 1
        if do_check:
            self.get_current_location().check_for_leaving(t)  # added this to re

    # override
    def set_position(self, new_x, new_y, is_updated_by_transporter=False):

        self.x = new_x
        self.y = new_y

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
            return
        if self.get_current_location() == self.home_loc:
            return
        if p == self:
            raise Exception("Can't latch to self")
        if len(self.latched_people) < self.max_latches:
            self.latched_people.append(p)
            self.latched_dst.append(des)
            p.latched_to = self
            Logger.log(f"{p.ID} latched to {self.ID}", 'w')
            return True
        else:
            Logger.log(f"Not enough space ({len(self.latched_people)}/{self.max_latches}) to latch onto!", 'e')
            return False

    def delatch_all(self):
        i = 0
        while i < (len(self.latched_people)):
            self.delatch(i)

    def delatch(self, idx):
        if type(idx) != int:
            idx = self.latched_people.index(idx)
        Logger.log(f"{self.latched_people[idx].ID} will be delatched "
                   f"from  transporter {self.ID} at {self.get_current_location()}")
        self.latched_people[idx].in_inter_trans = False
        self.latched_people[idx].latched_to = None
        self.latched_people.pop(idx)
        self.latched_dst.pop(idx)

    # override
    def update_route(self, root, t, new_route_classes=None, replace=False, keephome=True):
        Logger.log("Not IMPLEMENTED Transporter update route", 'c')
