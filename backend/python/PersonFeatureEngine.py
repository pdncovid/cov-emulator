import numpy as np

from backend.python.enums import Containment, PersonFeatures
from backend.python.location.Location import Location
from backend.python.point.Person import Person
from backend.python.Time import Time


class PersonFeatureEngine:

    @staticmethod
    def process_happiness(x, y, loc_ids, current_happiness, containment):
        happy_factor = 0
        if containment == Containment.NONE.value:
            happy_factor = 0
        elif containment == Containment.LOCKDOWN.value:
            happy_factor = -0.9
        elif containment == Containment.QUARANTINE.value:
            happy_factor = -0.3
        elif containment == Containment.QUARANTINECENTER.value:
            happy_factor = -0.5
        n = len(loc_ids[0])
        new_happiness = np.zeros(n)

        income = Person.features[:, PersonFeatures.daily_income.value]
        expense = Person.features[:, PersonFeatures.daily_expense.value]
        for p in range(n):
            locs = loc_ids[:, p]
            loc_dur = np.bincount(locs)
            containment_effect = happy_factor
            social_class_effect = (Person.features[p, PersonFeatures.social_class.value] - 5) / 10

            location_effect = 0
            for l in range(len(loc_dur)):
                if loc_dur[l] > 0:
                    location_effect += Location.all_locations[l].happiness_boost * loc_dur[l] * Time._scale
            location_effect = (location_effect/100)

            daily_income_effect = np.log(abs(income[p]-expense[p]))*np.sign(income[p]-expense[p])/25

            if containment_effect > 0:
                social_class_effect *= -1
            new_happiness[p] = current_happiness[p]*(1+containment_effect)*(1 + social_class_effect)*(1+ location_effect)*(1+ daily_income_effect)
        return new_happiness
