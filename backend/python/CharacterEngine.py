from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Time import Time
from backend.python.enums import *
from backend.python.location.Location import Location
from backend.python.point.Person import Person
import numpy as np


class CharacterEngine:

    @staticmethod
    def update_happiness(people, delta_eco_status, loc_ids, args):
        containment = ContainmentEngine.current_strategy
        for i, p in enumerate(people):
            cur_h = Person.features[p.ID, PF_happiness]
            cur_base_h = Person.features[p.ID, PF_base_happiness]
            if containment == "NONE":
                cur_h = cur_h - (cur_h - cur_base_h) * 0.1
            elif containment == "LOCKDOWN":
                cur_h = cur_h * 0.9
            elif containment == "QUARANTINE":
                cur_h = cur_h * 0.95
            elif containment == "QUARANTINECENTER":
                cur_h = cur_h * 0.92

            social_class_effect = (Person.features[p.ID, PF_social_class] - 5) / 10

            locs = loc_ids[:, p.ID]
            loc_dur = np.bincount(locs)
            location_effect = 0
            for l in range(len(loc_dur)):
                if loc_dur[l] > 0:
                    location_effect += Location.all_locations[l].happiness_boost * loc_dur[l] * Time._scale
            location_effect = (location_effect / 100)

            delta_eco_effect = max(1, min(-1, delta_eco_status[i]))  # clip by |1|

            cur_h = cur_h + delta_eco_effect + social_class_effect + location_effect

            Person.features[p.ID, PF_happiness] = cur_h

    @staticmethod
    def update_economy(people, args):
        containment = ContainmentEngine.current_strategy
        delta_eco_status = []
        for p in people:
            eco_status = Person.features[p.ID, PF_economic_status]
            income = Person.features[p.ID, PF_daily_income]
            s_class = Person.features[p.ID, PF_social_class]
            expense = income / s_class  # high social class tend to save because they have more money, low social class has to spend their daily wage
            if containment == "NONE":
                pass
            elif containment == "LOCKDOWN":
                expense *= 2
            elif containment == "QUARANTINE":
                expense *= 1.5
            elif containment == "QUARANTINECENTER":
                expense *= 1.1
            new_eco_status = eco_status + income - expense

            Person.features[p.ID, PF_economic_status] = new_eco_status
            delta_eco_status.append(new_eco_status - eco_status)
        return delta_eco_status
