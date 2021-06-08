import numpy as np


class MovementEngine:

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
        lc = point.current_loc
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
            if point.current_loc.depth > lc.depth:
                return point.current_loc.parent_location
            ln = point.get_next_target()
            while ln.depth != point.current_loc.depth + 1:
                ln = ln.parent_location
            return ln
        if point.current_loc.parent_location == ln.parent_location:
            return ln

        return point.current_loc.parent_location

    @staticmethod
    def random_move(location, p, vx_cap, vy_cap):
        p.x += p.vx
        p.y += p.vy

        if not location.is_inside(p.x, p.y):
            p.x -= p.vx
            p.y -= p.vy
            p.vx = -(p.vx + 1) / 2
            p.vy = -(p.vy + 1) / 2
            MovementEngine.move_towards(p, location.exit[0], location.exit[1])

        p.vx += np.random.rand() * 2 - 1
        p.vx = min(p.vx, vx_cap)
        p.vx = max(p.vx, -vx_cap)
        p.vy += np.random.rand() * 2 - 1
        p.vy = min(p.vy, vy_cap)
        p.vy = max(p.vy, -vy_cap)

    @staticmethod
    def move_towards(p, x, y):
        p.x += (x - p.x) / 10
        p.y += (y - p.y) / 10

    @staticmethod
    def is_close(p, xy, eps):
        return (p.x - xy[0]) ** 2 + (p.y - xy[1]) ** 2 < eps

    @staticmethod
    def containment(p, args):
        if args.containment == 0:
            pass
        if args.containment == 1:
            if np.random.rand() < 0.90:
                p.vx = 0
                p.vy = 0
