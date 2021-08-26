from backend.python.Time import Time


class Target:
    def __init__(self, loc, leaving_time, likely_trans):
        self.loc = loc
        self.leaving_time = leaving_time
        self.likely_trans = likely_trans
        self.leaving_time_beautiful = Time.i_to_time(leaving_time)

    def __repr__(self):
        d = {'loc': self.loc, 'lt': self.leaving_time, 'ltr': self.likely_trans}
        return ','.join(map(str, d.values()))

    def set_leaving_time(self, leaving_time):
        self.leaving_time = leaving_time
        self.leaving_time_beautiful = Time.i_to_time(leaving_time)

    def enter_person(self, p):
        self.loc.enter_person(p)

    def is_equal_wo_time(self, tar2):
        return self.loc == tar2.loc and self.likely_trans == tar2.likely_trans

    def __copy__(self):
        return type(self)(self.loc, self.leaving_time, self.likely_trans)
