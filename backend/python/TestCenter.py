import numpy as np
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
        if p.state == 1:
            boost_by_infected_period = min(args.asymptotic_t, t - p.infected_time) / args.asymptotic_t
            result = True if rnd < args.test_acc * boost_by_infected_period else False
        else:
            result = True if rnd > args.test_acc else False
        if result:
            p.tested_positive_time = t