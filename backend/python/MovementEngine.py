import numpy as np
from numba import njit


class MovementEngine:
    vx_cap = 1
    vy_cap = 1

    @staticmethod
    def random_move(p, args):
        p.x += p.vx
        p.vx += np.random.rand() * 2 - 1
        p.vx = min(p.vx, MovementEngine.vx_cap)
        p.vx = max(p.vx, -MovementEngine.vx_cap)

        p.y += p.vy
        p.vy += np.random.rand() * 2 - 1
        p.vy = min(p.vy, MovementEngine.vy_cap)
        p.vy = max(p.vy, -MovementEngine.vy_cap)

        if p.y < -args.H:
            p.y = -args.H
            p.vy *= -1
        if p.y > args.H:
            p.y = args.H
            p.vy *= -1

        if p.x < -args.W:
            p.x = -args.W
            p.vx *= -1
        if p.x > args.W:
            p.x = args.W
            p.vx *= -1

    @staticmethod
    def move(p, args):
        if args.mobility == 0:  # Random walk with acceleration
            MovementEngine.random_move(p, args)
            MovementEngine.containment(p, args)
        elif args.mobility == 1:  # Brownian motion
            pass

    @staticmethod
    def containment(p, args):
        if args.containment == 0:
            pass
        if args.containment == 1:
            if np.random.rand() < 0.90:
                p.vx = 0
                p.vy = 0
