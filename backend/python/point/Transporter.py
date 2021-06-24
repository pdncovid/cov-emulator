from backend.python.point.Person import Person


class Transporter(Person):

    def set_random_route(self, root, t, target_classes_or_objs=None):
        raise NotImplementedError()

    def __init__(self):
        super().__init__()
        self.latched_people = []
        self.latched_dst = []
        self.max_latches = 10

    # override
    def on_enter_location(self):
        i = 0
        while i < (len(self.latched_people)):
            if self.latched_dst[i] == self.get_current_location():
                print(f"{self.latched_people[i].ID} will be delatched from  transporter {self.ID} at {self.get_current_location()}")
                self.latched_people[i].is_latched = False
                self.latched_people.pop(i)
                self.latched_dst.pop(i)

                i -= 1
            i += 1

    # override
    def set_current_location(self, loc, t):
        self.current_loc = loc
        for p in self.latched_people:
            loc.enter_person(p, t, target_location=None)

    # override
    def set_position(self, new_x, new_y, is_updated_by_transporter=False):

        self.x = new_x
        self.y = new_y

        for latched_p in self.latched_people:
            latched_p.set_position(new_x, new_y, True)

    def latch(self, p, des):
        if p == self:
            raise Exception("Can't latch to self")
        if len(self.latched_people) < self.max_latches:
            self.latched_people.append(p)
            self.latched_dst.append(des)
            p.is_latched = True
            print(f"{p.ID} latched to {self.ID}")
            return True
        else:
            print("Not enough space to latch onto!")
            return False

