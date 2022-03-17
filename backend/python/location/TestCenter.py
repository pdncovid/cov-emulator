import numpy as np

from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Time import Time
from backend.python.Visualizer import Visualizer
from backend.python.enums import State, TestSpawn, PersonFeatures


class TestCenter:
    testresultdelay = Time.get_duration(24)
    test_freq_days = 3

    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

        self.vx = 0
        self.vy = 0

        self.max_tests = 100
        self.daily_tests = 0

    def on_reset_day(self):
        self.daily_tests = 0

    def test(self, p, t, test_type='PCR'):
        mu = 7
        sig = 2
        if p.features[p.ID, PersonFeatures.state.value] == State.INFECTED.value:
            if p.is_tested_positive():
                return
            if t - p.features[p.ID, PersonFeatures.last_tested_time.value] < TestCenter.test_freq_days * Time.DAY:
                return
            rnd = np.random.rand()
            test_acc = np.exp(-np.power((t - p.features[p.ID, PersonFeatures.infected_time.value]) / Time.DAY - mu, 2.) / (2 * np.power(sig, 2.)))
            result = True if rnd < test_acc else False
        else:
            result = False  # True if rnd > args.test_acc else False
        if result:
            p.features[p.ID, PersonFeatures.tested_positive_time.value] = t + TestCenter.testresultdelay
            ContainmentEngine.on_infected_identified(p)
        ContainmentEngine.check_tested_positive_actions()  # might be slow
        p.features[p.ID, PersonFeatures.last_tested_time.value] = t

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
