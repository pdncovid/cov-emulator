class Target:
    def __init__(self, loc, leaving_time, likely_trans):
        self.loc = loc
        self.leaving_time = leaving_time
        self.likely_trans = likely_trans

    def __repr__(self):
        d = {'loc': self.loc, 'lt': self.leaving_time, 'ltr': self.likely_trans}
        return ','.join(map(str, d.values()))

    def enter_person(self, p, target_location=None):
        self.loc.enter_person(p, target_location)

    def __copy__(self):
        return type(self)(self.loc, self.leaving_time, self.likely_trans)
