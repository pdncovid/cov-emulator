from backend.python.enums import Containment
from backend.python.Time import Time


class ContainmentEngine:
    testresultdelay = Time.get_duration(5)
    quarantineduration = Time.get_duration(24 * 2)

    @staticmethod
    def can_go_there(p, current_l, next_l):
        # todo add any containment strategy logic
        if current_l.depth >= next_l.depth:
            move_out = True
        else:
            move_out = False

        return not current_l.quarantined or not move_out or p.is_recovered()

    @staticmethod
    def check_to_update_route(p, root, containment, t):
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
                from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
                for l in p.route:
                    if isinstance(l, COVIDQuarantineZone):
                        return False
                p.update_route(root, t, ContainmentEngine.get_containment_route_for_tested_positives(p), replace=True)
                return False

    @staticmethod
    def check_location_state_updates(root, t):
        def f(r):
            if r.quarantined and t - r.quarantined_time > ContainmentEngine.quarantineduration:
                r.set_quarantined(False, t)
            for ch in r.locations:
                f(ch)

        f(root)

    @staticmethod
    def get_containment_route_for_tested_positives(p):

        from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
        return [COVIDQuarantineZone]
