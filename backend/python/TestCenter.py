import numpy as np

from backend.python.enums import State


class TestCenter:

    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

        self.vx = 0
        self.vy = 0

    @staticmethod
    def test(p, t, args):
        rnd = np.random.rand()
        if p.state == State.INFECTED.value:
            if p.tested_positive_time > 0:
                return
            else:
                boost_by_infected_period = min(args.asymptotic_t, t - p.infected_time) / args.asymptotic_t
                result = True if rnd < args.test_acc * boost_by_infected_period else False
        else:
            result = False  # True if rnd > args.test_acc else False
        if result:
            p.tested_positive_time = t