import numpy as np

from backend.python.Time import Time


class MovementEngine:

    @staticmethod
    def move_people(all_people):
        _p = all_people[0]
        is_latched = [p.latched_to is not None for p in _p.all_people]

        is_in_loc_move = np.expand_dims(_p.all_destinations == -1, -1)

        # inside location random movement
        new_xy = _p.all_positions + _p.all_velocities * is_in_loc_move
        is_outside = np.sum((new_xy - _p.all_current_loc_positions) ** 2, 1) > _p.all_current_loc_radii ** 2
        is_outside = is_outside * is_in_loc_move[:, 0]
        _p.all_velocities[is_outside] = -(_p.all_velocities[is_outside] + 1) / 2
        new_xy[is_outside] = _p.all_positions[is_outside]

        # movement to other location
        new_xy = np.where(is_in_loc_move,
                          new_xy,  # if in location movement
                          np.where(np.expand_dims(np.sum((_p.all_destination_exits - _p.all_positions) ** 2,
                                                         1) < _p.all_current_loc_vcap ** 2, -1),
                                   _p.all_destination_exits,  # if between location move reaches destination
                                   _p.all_positions + np.sign(
                                       _p.all_destination_exits - _p.all_positions) * np.expand_dims(
                                       _p.all_current_loc_vcap, -1)))# todo unlatched people wont wait!!!!!

        for idx, p in enumerate(all_people):
            if is_latched[idx]:
                continue
            p.set_position(new_xy[p.ID, 0], new_xy[p.ID, 1])
            if MovementEngine.is_close(p, p.all_destination_exits[p.ID], eps=p.current_trans.destination_reach_eps) and \
                    is_in_loc_move[p.ID] == False:
                p.get_current_location().all_locations[p.all_destinations[p.ID]].enter_person(
                    p)  # destination point reached
                p.in_inter_trans = False


        new_v = _p.all_velocities + np.random.random((len(_p.all_velocities), 2))
        _p.all_velocities = np.clip(new_v, -np.expand_dims(_p.all_current_loc_vcap, -1),
                                    np.expand_dims(_p.all_current_loc_vcap, -1))

        # t = Time.get_time()
        # for p in all_people:
        #     p.current_trans.move(p, t)

    @staticmethod
    def process_people_switching(loc, t):
        loc.check_for_leaving(t)

        if len(loc.locations) == 0:
            if loc.override_transport is None:
                raise Exception("Leaf locations should always override transport")
        else:
            for location in loc.locations:
                MovementEngine.process_people_switching(location, t)

    @staticmethod
    def find_lcp_location(point):
        lc = point.get_current_location()
        ln = point.get_next_target().loc

        dc, dn = lc.depth, ln.depth

        while lc.parent_location != ln.parent_location:
            if dc > dn:
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
        # path = path_1 + [lc] + path_2  # this will add root of subtree to path!
        path = path_1 + path_2[::-1]
        return path

    @staticmethod
    def get_next_target_path(point):

        lc = point.get_current_location()
        ln = point.get_next_target().loc
        return MovementEngine.get_path(lc, ln)

    @staticmethod
    def random_move(location, p, v_cap):
        new_x, new_y = p.all_positions[p.ID] + p.all_velocities[p.ID]

        if location.is_inside(new_x, new_y):
            p.set_position(new_x, new_y)
        else:
            p.all_velocities[p.ID] = -(p.all_velocities[p.ID] + 1) / 2
            MovementEngine.move_towards(p, location.exit, v_cap)

        p.all_velocities[p.ID] += np.random.rand(2) * 2 - 1
        p.all_velocities[p.ID] = np.clip(p.all_velocities[p.ID], -v_cap, v_cap)

    @staticmethod
    def move_towards(p, xy, v_cap):
        x_new, y_new = np.where(abs(xy - p.all_positions[p.ID]) < v_cap, xy,
                                p.all_positions[p.ID] + np.sign(xy - p.all_positions[p.ID]) * v_cap)

        p.set_position(x_new, y_new)

    @staticmethod
    def is_close(p, xy, eps):
        return (p.all_positions[p.ID][0] - xy[0]) ** 2 + (p.all_positions[p.ID][1] - xy[1]) ** 2 < eps ** 2

    @staticmethod
    def containment(p, args):
        if args.containment == 0:
            pass
        if args.containment == 1:
            if np.random.rand() < 0.90:
                p.all_velocities[p.ID] = [0, 0]
