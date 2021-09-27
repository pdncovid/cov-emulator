from backend.python.location.GatheringPlace import GatheringPlace


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
            if not self.select_criteria(p) or p.is_dead():
                continue
            for tar in p.route:
                if isinstance(tar.loc, GatheringPlace):
                    break
            else:
                selected.append(p)
            if len(selected) == self.capacity:
                break
        return selected
