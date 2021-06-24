import numpy as np


class MovementEngine:

    @staticmethod
    def move_people(all_transports, t):
        for trans in all_transports:
            trans.move_people(t)

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
        ln = point.get_next_target()

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
        ln = point.get_next_target()
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
            ln = point.get_next_target()
            while ln.depth != point.get_current_location().depth + 1:
                ln = ln.parent_location
            return ln
        if point.get_current_location().parent_location == ln.parent_location:
            return ln

        return point.get_current_location().parent_location

    @staticmethod
    def get_next_target_path(point):

        lc = point.get_current_location()
        ln = point.get_next_target()
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
        path = path_1 + path_2
        return path

    @staticmethod
    def random_move(location, p, vx_cap, vy_cap):
        new_x = p.x + p.vx
        new_y = p.y + p.vy

        if location.is_inside(new_x, new_y):
            p.set_position(new_x, new_y)
        else:
            p.vx = -(p.vx + 1) / 2
            p.vy = -(p.vy + 1) / 2
            MovementEngine.move_towards(p, location.exit[0], location.exit[1], vx_cap, vy_cap)

        p.vx += np.random.rand() * 2 - 1
        p.vx = min(p.vx, vx_cap)
        p.vx = max(p.vx, -vx_cap)
        p.vy += np.random.rand() * 2 - 1
        p.vy = min(p.vy, vy_cap)
        p.vy = max(p.vy, -vy_cap)

    @staticmethod
    def move_towards(p, x, y, vx_cap, vy_cap):
        p.set_position(p.x + (x - p.x) / vx_cap, p.y + (y - p.y) / vy_cap)

    @staticmethod
    def is_close(p, xy, eps):
        return (p.x - xy[0]) ** 2 + (p.y - xy[1]) ** 2 < eps**2

    @staticmethod
    def containment(p, args):
        if args.containment == 0:
            pass
        if args.containment == 1:
            if np.random.rand() < 0.90:
                p.vx = 0
                p.vy = 0
