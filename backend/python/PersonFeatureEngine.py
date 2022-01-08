import numpy as np

from backend.python.enums import Containment, PersonFeatures
from backend.python.point.Person import Person


class PersonFeatureEngine:

    @staticmethod
    def process_happiness(x,y,loc_ids, current_happiness, containment):
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
        for p in range(n):
            locs = loc_ids[:, p]
            loc_dur = np.bincount(locs)
            containment_effect = current_happiness[p] * happy_factor
            social_class_effect = current_happiness[p] * (Person.features[p, PersonFeatures.social_class.value]-5)/10


            if containment_effect > 0:
                social_class_effect *= -1
            new_happiness[p] = current_happiness[p] + containment_effect + social_class_effect

