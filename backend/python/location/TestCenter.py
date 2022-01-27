import numpy as np

from backend.python.Time import Time
from backend.python.Visualizer import Visualizer
from backend.python.enums import State, TestSpawn


class TestCenter:
    asymptotic_t = -1
    test_acc = -1
    testresultdelay = Time.get_duration(24)
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

        self.vx = 0
        self.vy = 0

        self.max_tests = 100
        self.daily_tests = 0

    @staticmethod
    def set_parameters(asymptotic_t, test_acc):
        TestCenter.asymptotic_t = asymptotic_t
        TestCenter.test_acc = test_acc

    def on_reset_day(self):
        self.daily_tests = 0

    def test(self, p, t):
        rnd = np.random.rand()
        if p.state == State.INFECTED.value:
            if p.tested_positive_time > 0:
                return
            else:
                boost_by_infected_period = min(TestCenter.asymptotic_t, t - p.infected_time) / TestCenter.asymptotic_t
                result = True if rnd < TestCenter.test_acc * boost_by_infected_period else False
        else:
            result = False  # True if rnd > args.test_acc else False
        if result:
            p.set_tested_positive()
            p.tested_positive_time = t+TestCenter.testresultdelay

    @staticmethod
    def spawn_test_center(method, points, test_centers, h, w, r, threshold):
        if method == TestSpawn.RANDOM.value:
            if np.random.rand() < 0.001:
                return TestCenter(np.random.randint(-w, w), np.random.randint(-h, h), np.random.normal(r, 2))
        if method == TestSpawn.HEATMAP.value:
            xx, yy, zz = Visualizer.get_heatmap(points, h, w)
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
