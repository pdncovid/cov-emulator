
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
                if tar.loc.class_name=='GatheringPlace':
                    break
            else:
                selected.append(p)
            if len(selected) == self.capacity:
                break
        return selected

    def __repr__(self):
        return f"Event: Day={self.day} Time={self.time} Dur={self.duration} Loc={self.loc} Cap={self.capacity}"