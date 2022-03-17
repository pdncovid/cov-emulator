from backend.python.Logger import Logger
from backend.python.enums import Containment, PersonFeatures
from backend.python.Time import Time


class ContainmentEngine:
    quarantineduration = Time.get_duration(24 * 14)
    current_strategy = Containment.NONE.name
    current_rosters = 1

    result_queue = []

    @staticmethod
    def on_infected_identified(p):
        ContainmentEngine.result_queue.append(p)
        Logger.log(f"{p.ID} will be identified as infected. "
                   f"Test result on {p.features[p.ID, PersonFeatures.tested_positive_time.value]} "
                   f"Home {p.home_loc}", 'c')

    @staticmethod
    def check_tested_positive_actions():
        t = Time.get_time()
        i = 0
        while i < len(ContainmentEngine.result_queue):
            person = ContainmentEngine.result_queue[i]
            if person.features[person.ID, PersonFeatures.tested_positive_time.value] < t:
                if ContainmentEngine.current_strategy == Containment.QUARANTINE.name:
                    person.home_loc.set_quarantined(True, t)

                    others_in_home = []
                    for _p in person.all_people:
                        if _p.home_loc == person.home_loc:
                            others_in_home.append(_p)
                    Logger.log(f"({person.ID}'s home) {person.home_loc} quarantined. Others ({' '.join(map(str, others_in_home))})", 'c')

                elif ContainmentEngine.current_strategy == Containment.QUARANTINECENTER.name:
                    person.home_loc.set_quarantined(True, t)  # TODO quarantine home ?

                ContainmentEngine.result_queue.pop(i)
                i -= 1
            i += 1

    @staticmethod
    def can_go_there(p, current_l, next_l):
        if current_l == next_l:
            return True
        if ContainmentEngine.current_strategy == Containment.NONE.name:
            return True

        # todo add any containment strategy logic
        if current_l.depth >= next_l.depth:
            move_out = True
        else:
            move_out = False

        return not current_l.quarantined or not move_out #or p.is_recovered()

    @staticmethod
    def update_route_according_to_containment(p, root, containment, t):
        if p.is_tested_positive() and p.is_infected():
            if containment == Containment.NONE.name:
                return False
            elif containment == Containment.LOCKDOWN.name:
                root.set_quarantined(True, t, recursive=True)
                return True
            elif containment == Containment.QUARANTINE.name:
                p.route[0].loc.set_quarantined(True, t)
                # todo when moved to quarantined home, doesnt goto cov center
                # p.update_route(root, 0, ContainmentEngine.get_containment_route_for_tested_positives(p), replace=True)
                return False
            elif containment == Containment.QUARANTINECENTER.name:
                for tar in p.route:
                    if tar.loc.class_name == 'COVIDQuarantineZone':
                        return False
                p.update_route(root, t, ContainmentEngine.get_containment_route_for_tested_positives(p), replace=True)
                return False

    @staticmethod
    def check_location_state_updates(root, t):
        def f(r):
            if r.quarantined and t - r.quarantined_time > ContainmentEngine.quarantineduration:
                Logger.log(f"{r.ID} is removed from quarantine because time out {t} - {r.quarantined_time} > {ContainmentEngine.quarantineduration}", 'c')
                r.set_quarantined(False, t)
            for ch in r.locations:
                f(ch)

        f(root)

    @staticmethod
    def get_containment_route_for_tested_positives(p):
        return ['COVIDQuarantineZone']

    @staticmethod
    def assign_roster_days(people, roster_groups):
        if ContainmentEngine.current_strategy == Containment.ROSTER.name and ContainmentEngine.current_rosters == roster_groups:
            return
        ContainmentEngine.current_rosters = roster_groups
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
                group_start = i % roster_groups
                while group_start < 7:
                    work_groups[wl][i].roster_days.append(group_start)
                    if n <= roster_groups:
                        group_start += n
                    else:
                        group_start += roster_groups
