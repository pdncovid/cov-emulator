
class GatherEvent:
    def __init__(self, day, time, duration, loc, capacity, select_criteria):
        self.day = day
        self.time = time
        self.duration = duration
        self.loc = loc
        self.capacity = capacity
        self.select_criteria = select_criteria

    def select_people(self, people):
        selected = []
        for p in people:
            if self.select_criteria(p) and not p.is_dead():
                selected.append(p)
        return selected