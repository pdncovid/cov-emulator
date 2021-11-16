import numpy as np

from backend.python.functions import bs


class TestingEngine:

    @staticmethod
    def testing_procedure(points, test_centers, t):
        from backend.python.point.Person import Person
        x, y = Person.all_positions[:, 0], Person.all_positions[:, 1]
        xs_idx = np.argsort(x)
        ys_idx = np.argsort(y)
        xs = x[xs_idx]
        ys = y[ys_idx]

        test_subjects = set()
        tested_on = np.zeros((len(points)), dtype=int)

        for i in range(len(test_centers)):  # iterate through test centers

            r = test_centers[i].r

            x_idx_r = bs(xs, test_centers[i].x + r)
            x_idx_l = bs(xs, test_centers[i].x - r)  # + 1

            y_idx_r = bs(ys, test_centers[i].y + r)
            y_idx_l = bs(ys, test_centers[i].y - r)  # + 1

            close_points = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r])
            for close_point in close_points:
                test_subjects.add(close_point)
                tested_on[close_point] = i
        test_count = np.zeros(len(test_centers), dtype=int)
        for p_idx in test_subjects:
            tc = test_centers[tested_on[p_idx]]
            if test_count[tested_on[p_idx]] >= tc.max_tests:
                continue
            if tc.daily_tests >= tc.max_tests:
                continue
            tc.test(points[p_idx], t)
            tc.daily_tests += 1
            test_count[tested_on[p_idx]] += 1
