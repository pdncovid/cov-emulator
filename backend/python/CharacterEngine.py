from backend.python.Time import Time
from backend.python.enums import PersonFeatures, Containment
from backend.python.location.Location import Location
from backend.python.point.Person import Person
import numpy as np


class CharacterEngine:

    @staticmethod
    def update_happiness(people, delta_eco_status, loc_ids, args):
        containment = args.containment
        for i, p in enumerate(people):
            cur_h = Person.features[p.ID, PersonFeatures.happiness.value]
            cur_base_h = Person.features[p.ID, PersonFeatures.base_happiness.value]
            if containment == Containment.NONE.value:
                cur_h = cur_h - (cur_h - cur_base_h) * 0.1
            elif containment == Containment.LOCKDOWN.value:
                cur_h = cur_h * 0.9
            elif containment == Containment.QUARANTINE.value:
                cur_h = cur_h * 0.95
            elif containment == Containment.QUARANTINECENTER.value:
                cur_h = cur_h * 0.92

            social_class_effect = (Person.features[p.ID, PersonFeatures.social_class.value] - 5) / 10

            locs = loc_ids[:, p.ID]
            loc_dur = np.bincount(locs)
            location_effect = 0
            for l in range(len(loc_dur)):
                if loc_dur[l] > 0:
                    location_effect += Location.all_locations[l].happiness_boost * loc_dur[l] * Time._scale
            location_effect = (location_effect / 100)

            delta_eco_effect = max(1, min(-1, delta_eco_status[i]))  # clip by |1|

            cur_h = cur_h + delta_eco_effect + social_class_effect + location_effect

            Person.features[p.ID, PersonFeatures.happiness.value] = cur_h

    @staticmethod
    def update_economy(people, args):
        containment = args.containment
        delta_eco_status = []
        for p in people:
            eco_status = Person.features[p.ID, PersonFeatures.economic_status.value]
            income = Person.features[p.ID, PersonFeatures.daily_income.value]
            s_class = Person.features[p.ID, PersonFeatures.social_class.value]
            expense = income / s_class  # high social class tend to save because they have more money, low social class has to spend their daily wage
            if containment == Containment.NONE.value:
                pass
            elif containment == Containment.LOCKDOWN.value:
                expense *= 2
            elif containment == Containment.QUARANTINE.value:
                expense *= 1.5
            elif containment == Containment.QUARANTINECENTER.value:
                expense *= 1.1
            new_eco_status = eco_status + income - expense

            Person.features[p.ID, PersonFeatures.economic_status.value] = new_eco_status
            delta_eco_status.append(new_eco_status - eco_status)
        return delta_eco_status
