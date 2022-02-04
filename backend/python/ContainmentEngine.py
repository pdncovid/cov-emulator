import math

from backend.python.enums import Containment
from backend.python.Time import Time


class ContainmentEngine:

    quarantineduration = Time.get_duration(24 * 14)

    @staticmethod
    def can_go_there(p, current_l, next_l):
        if current_l == next_l:
            return True
        # todo add any containment strategy logic
        if current_l.depth >= next_l.depth:
            move_out = True
        else:
            move_out = False

        return not current_l.quarantined or not move_out or p.is_recovered()

    @staticmethod
    def update_route_according_to_containment(p, root, containment, t):
        if p.is_tested_positive() and p.is_infected():
            if containment == Containment.NONE.value:
                return False
            elif containment == Containment.LOCKDOWN.value:
                root.set_quarantined(True, t, recursive=True)
                return True
            elif containment == Containment.QUARANTINE.value:
                p.route[0].loc.set_quarantined(True, t)
                # todo when moved to quarantined home, doesnt goto cov center
                # p.update_route(root, 0, ContainmentEngine.get_containment_route_for_tested_positives(p), replace=True)
                return False
            elif containment == Containment.QUARANTINECENTER.value:
                from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
                for tar in p.route:
                    if isinstance(tar.loc, COVIDQuarantineZone):
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

    @staticmethod
    def assign_roster_days(people, root, args):
        roster_groups = args.roster_groups
        work_groups = {}
        for p in people:
            wl = p.work_loc
            if wl in work_groups.keys():
                work_groups[wl].append(p)
            else:
                work_groups[wl] = [p]
        for wl in work_groups.keys():
            n = len(work_groups[wl])
            # group_size = math.ceil(n / roster_groups)
            for i in range(n):
                group_start = i%roster_groups
                while group_start < 7:
                    work_groups[wl][i].roster_days.append(group_start)
                    if n <= roster_groups:
                        group_start += n
                    else:
                        group_start += roster_groups

