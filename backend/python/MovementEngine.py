import numpy as np

from backend.python.Logger import Logger
from backend.python.Time import Time
from backend.python.enums import *
from backend.python.transport.Movement import Movement


class MovementEngine:
    min_v_cap_frac = 0.15

    @staticmethod
    def move_people(all_people):
        from backend.python.point.Person import Person
        _p = Person

        is_in_loc_move = np.expand_dims(_p.all_destinations == -1, -1)

        vxy = _p.features[:, [PF_vx, PF_vy]]
        # new_v = 0.5*_p.all_velocities + (_p.all_velocities*0.25+1)*np.random.random((len(_p.all_velocities), 2))
        new_v = np.expand_dims(_p.all_current_loc_vcap, -1) * (np.random.random((len(vxy), 2)) * 2 - 1)  # TODO
        # v might be too small
        new_v = np.sign(new_v) * np.clip(np.abs(new_v),
                                         np.expand_dims(_p.all_current_loc_vcap, -1) * MovementEngine.min_v_cap_frac,
                                         np.expand_dims(_p.all_current_loc_vcap, -1))
        vxy = new_v

        xy = _p.features[:, [PF_px, PF_py]]
        # inside location random movement
        new_xy = xy + vxy * is_in_loc_move
        is_outside = np.sum((new_xy - _p.all_current_loc_positions) ** 2, 1) > _p.all_current_loc_radii ** 2
        is_outside = is_outside * is_in_loc_move[:, 0]
        vxy[is_outside] = -(vxy[is_outside] + 1) / 2
        new_xy[is_outside] = (np.random.random(xy.shape) * (
                2 ** 0.5 * np.expand_dims(_p.all_current_loc_radii, -1)) + _p.all_current_loc_positions)[is_outside]

        _p.features[:, [PF_vx, PF_vy]] = vxy

        # movement to other location
        new_xy_inter_loc = np.where(
            np.expand_dims(np.sum((_p.all_destination_exits - xy) ** 2, 1) < _p.all_current_loc_vcap ** 2,
                           -1),
            _p.all_destination_exits,  # if between location move reaches destination
            xy + np.sign(_p.all_destination_exits - xy) * np.expand_dims(
                _p.all_current_loc_vcap, -1))

        new_xy = np.where(is_in_loc_move, new_xy, new_xy_inter_loc)

        from backend.python.point.Transporter import Transporter
        from backend.python.transport.MovementByTransporter import MovementByTransporter
        for idx, p in enumerate(all_people):
            if p.is_dead():
                continue
            if isinstance(p.current_trans, MovementByTransporter) and not isinstance(p, Transporter):
                continue
            if isinstance(p.current_trans, MovementByTransporter):
                p.set_position(new_xy[p.ID, 0], new_xy[p.ID, 1])
            else:
                p.set_position(new_xy[p.ID, 0], new_xy[p.ID, 1], force=True)
            if _p.all_destinations[p.ID] == -1:  # in location move
                continue
            if MovementEngine.is_close(p, _p.all_destination_exits[p.ID], eps=p.current_trans.destination_reach_eps) and \
                    is_in_loc_move[p.ID] == False:
                # destination point reached
                p.get_current_location().all_locations[p.all_destinations[p.ID]].on_destination_reached(p)

                # p.in_inter_trans = False

        # t = Time.get_time()
        # for p in all_people:
        #     p.current_trans.move(p, t)

    @staticmethod
    def process_people_switching2(loc, t):
        loc.check_for_leaving(t)

        if len(loc.locations) == 0:
            if loc.override_transport is None:
                raise Exception("Leaf locations should always override transport")
        else:
            for location in loc.locations:
                MovementEngine.process_people_switching(location, t)

    @staticmethod
    def process_people_switching(people, t):
        n_overtime = 0
        from backend.python.point.Transporter import Transporter
        wait_lvl0 = Time.get_duration(0.25)
        wait_lvl1 = Time.get_duration(0.5)
        for p in people:
            # check if the time spent in the current location is above
            # the point's staying threshold for that location
            if p.is_dead():
                continue
            if t >= p.current_loc_leave and p.latched_to is None:
                if not isinstance(p, Transporter):
                    if p.is_day_finished and p.get_current_location() == p.route[-1].loc:
                        continue
                    # # waiting too long in this place!!!
                    dt_leave = t - p.current_loc_leave
                    dt_enter = t - p.current_loc_enter
                    if dt_leave > wait_lvl1 and dt_enter > wait_lvl1 and not p.current_trans.class_name == 'Taxi':
                        # Logger.log(
                        #     f"OT {p.class_name}-{p} @ {p.get_current_location().class_name} since {Time.i_to_datetime(p.current_loc_leave)} "
                        #     f"for {Time.i_to_minutes(t - p.current_loc_leave)} "
                        #     f"-> {MovementEngine.find_next_location(p).class_name} [{p.get_next_target().loc.class_name}] "
                        #     f"({p.current_target_idx}/{len(p.route) - 1}) "
                        #     f"Movement {p.current_trans} -> Taxi"
                        #     , 'e'
                        # )
                        Movement.all_instances['Taxi'].add_point_to_transport(p)
                        p.get_current_location().leave_this_location(p, force=True)
                        n_overtime += 1
                        continue
                p.get_current_location().leave_this_location(p)

        return n_overtime

    @staticmethod
    def find_lcp_location(point):
        lc = point.get_current_location()
        ln = point.get_next_target().loc
        dc, dn = lc.depth, ln.depth

        while lc.parent_location != ln.parent_location:
            if dc < dn:
                dn -= 1
                ln = ln.parent_location
            else:
                dc -= 1
                lc = lc.parent_location
        return lc

    @staticmethod
    def find_next_location(point):
        lc = point.get_current_location()
        ln = point.get_next_target().loc
        if lc == ln:
            return ln

        dc, dn = lc.depth, ln.depth

        while dc != dn:
            if dc < dn:
                dn -= 1
                ln = ln.parent_location
            else:
                dc -= 1
                lc = lc.parent_location
        if lc == ln:  # same line
            if point.get_current_location().depth > lc.depth:
                return point.get_current_location().parent_location
            ln = point.get_next_target().loc
            while ln.depth != point.get_current_location().depth + 1:
                ln = ln.parent_location
            return ln
        if point.get_current_location().parent_location == ln.parent_location:
            return ln

        return point.get_current_location().parent_location

    @staticmethod
    def get_path(lc, ln):
        if lc == ln:
            return [ln]

        path_2 = []
        path_1 = []
        while lc != ln:
            if lc.depth < ln.depth:
                path_2 = path_2 + [ln]
                ln = ln.parent_location
            else:
                path_1 = path_1 + [lc]
                lc = lc.parent_location

        if lc.depth != 0 and (len(path_2) == 0 or len(path_1) == 0):  # if not this will add root of tree to path!
            path = path_1 + [lc] + path_2[::-1]
        else:
            path = path_1 + path_2[::-1]

        return path

    @staticmethod
    def get_next_target_path(point):

        lc = point.get_current_location()
        ln = point.get_next_target().loc
        return MovementEngine.get_path(lc, ln)

    @staticmethod
    def get_time_to_move(loc1, loc2, p):
        t = 0
        path = MovementEngine.get_path(loc1, loc2)
        cur = loc1
        for loc in path:
            t += MovementEngine._get_time_to_move_adj(cur, loc, p)
            cur = loc
        return t

    @staticmethod
    def _get_time_to_move_adj(loc1, loc2, p):
        if loc1 == loc2:
            return 0
        dist = loc1.get_distance_to(loc2) * 1  # todo : what is the time to travel between locations
        if loc1.depth == loc2.depth:
            return dist / MovementEngine.get_movement_method(loc1.parent_location, p).vcap
        if loc1.depth < loc2.depth:
            return dist / MovementEngine.get_movement_method(loc1, p).vcap
        if loc2.depth < loc1.depth:
            return dist / MovementEngine.get_movement_method(loc2, p).vcap
        raise Exception("Cannot reach here")

    @staticmethod
    def set_movement_method(loc, p):
        if not p.latched_to:
            # add the person to the default transportation system, if the person is not latched to someone else.
            trans = MovementEngine.get_movement_method(loc, p)
            trans.add_point_to_transport(p)

    @staticmethod
    def get_movement_method(moving_loc, p):
        trans = p.main_trans

        from backend.python.point.Transporter import Transporter
        if isinstance(p, Transporter):
            if p.is_day_finished:
                trans = moving_loc.override_transport
        else:
            if moving_loc.override_transport is not None:
                if moving_loc.override_transport.override_level <= p.main_trans.override_level:
                    trans = moving_loc.override_transport
            if p.home_loc == moving_loc or p.home_weekend_loc == moving_loc:
                trans = moving_loc.override_transport
        return trans

    @staticmethod
    def is_close(p, xy, eps):
        x = p.features[p.ID, PF_px]
        y = p.features[p.ID, PF_py]
        return (x - xy[0]) ** 2 + (y - xy[1]) ** 2 < eps ** 2

    @staticmethod
    def containment(p, args):
        if args.containment == 0:
            pass
        if args.containment == 1:
            if np.random.rand() < 0.90:
                p.features[p.ID, PF_vx] = 0
                p.features[p.ID, PF_vy] = 0
