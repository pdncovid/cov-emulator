from backend.python.enums import Containment
from backend.python.functions import get_duration
from backend.python.location.Location import Location
from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone


class ContainmentEngine:

    testresultdelay = get_duration(5)
    quarantineduration = get_duration(24*2)

    @staticmethod
    def check(p, root,containment,t):
        if p.is_tested_positive() and p.is_infected() and t - p.tested_positive_time > ContainmentEngine.testresultdelay:
            if containment == Containment.NONE.value:
                return False
            elif containment == Containment.LOCKDOWN.value:
                root.set_quarantined(True, t, recursive=True)
                return True
            elif containment == Containment.QUARANTINE.value:
                p.route[0].set_quarantined(True, t)
                # todo when moved to quarantined home, doesnt goto cov center
                # p.update_route(root, 0, ContainmentEngine.get_containment_route_for_tested_positives(p), replace=True)
                return False
            elif containment == Containment.QUARANTINECENTER.value:
                # todo check if p is in quarantinecenter. if so do not modify route
                p.update_route(root, t, ContainmentEngine.get_containment_route_for_tested_positives(p), replace=True)
                return False

    @staticmethod
    def check_locations(root, t):
        def f(r: Location):
            if r.quarantined and t - r.quarantined_time > ContainmentEngine.quarantineduration:
                r.set_quarantined(False, t)
            for ch in r.locations:
                f(ch)

        f(root)

    @staticmethod
    def get_containment_route_for_tested_positives(p):

        return [COVIDQuarantineZone]
