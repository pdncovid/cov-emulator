import numpy as np

from backend.python.Visualizer import get_heatmap
from backend.python.enums import State, TestSpawn


class TestCenter:

    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

        self.vx = 0
        self.vy = 0

        self.max_tests = 100

    def test(self, p, t, args):
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

    @staticmethod
    def spawn_test_center(method, points, test_centers, h, w, r, threshold):
        if method == TestSpawn.RANDOM.value:
            if np.random.rand() < 0.001:
                return TestCenter(np.random.randint(-w, w), np.random.randint(-h, h), np.random.normal(r, 2))
        if method == TestSpawn.HEATMAP.value:
            xx, yy, zz = get_heatmap(points, h, w)
            xx = xx.ravel()
            yy = yy.ravel()
            zz = zz.ravel()
            zz_sort_idx = np.argsort(zz)

            for i in range(zz.shape[0] - 1, -1, -1):
                x = xx[zz_sort_idx[i]]
                y = yy[zz_sort_idx[i]]
                z = zz[zz_sort_idx[i]]
                in_test = False
                if z < threshold:
                    break
                for tc in test_centers:
                    if (tc.x - x) ** 2 + (tc.y - y) ** 2 < tc.r ** 2:
                        in_test = True
                        break
                if not in_test:
                    return TestCenter(x, y, np.random.normal(r, 2))
