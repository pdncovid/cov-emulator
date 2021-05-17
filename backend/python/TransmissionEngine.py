import numpy as np

from backend.python.enums import State
from backend.python.functions import bs
from numba import njit


class TransmissionEngine:
    debug = True

    @staticmethod
    @njit
    def get_close_contacts_and_distance(x, y, state, r):
        contacts = np.zeros(len(x))
        distance = np.ones(len(x)) * 1000
        sourceid = np.zeros(len(x), dtype=np.int64)

        xs_idx = np.argsort(x)
        ys_idx = np.argsort(y)
        xs = x[xs_idx]
        ys = y[ys_idx]
        # xs = np.take_along_axis(x, xs_idx, 0)
        # ys = np.take_along_axis(y, ys_idx, 0)

        procesed = 0
        for i in np.where(state == State.INFECTED.value)[0]:
            # iterate through infected people only to increase speed
            # if state[i] != State.INFECTED.value:
            #     continue
            # infect to closest points

            x_idx_r = bs(xs, x[i] + r)
            x_idx_l = bs(xs, x[i] - r)

            y_idx_r = bs(ys, y[i] + r)
            y_idx_l = bs(ys, y[i] - r)

            close_points_idx = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r])
            procesed += len(close_points_idx)
            close_points_idx = close_points_idx[state[close_points_idx] == State.SUSCEPTIBLE.value]

            d = np.sqrt(np.power(x[close_points_idx] - x[i], 2) + np.power(y[close_points_idx] - y[i], 2))

            close_points_idx = close_points_idx[d < r]
            d = d[d < r]

            contacts[close_points_idx] += 1
            sourceid[close_points_idx[d < distance[close_points_idx]]] = i
            distance[close_points_idx] = np.minimum(d, distance[close_points_idx])
        # if TransmissionEngine.debug:
        #     print(f"Processed {procesed}")
        return contacts, distance, sourceid

    @staticmethod
    def transmit_disease(points, contacts, distance, sourceid, beta, common_p, t):
        valid = np.where(contacts > 0)[0]
        validsourceid = sourceid[valid]
        infected_duration = []
        for i in validsourceid:
            infected_duration.append(t - points[i].infected_time)
        infected_duration = np.array(infected_duration)
        tr_p = TransmissionEngine.get_transmission_p(beta, distance[valid], infected_duration)
        rand = np.random.rand(len(valid))

        c = 0
        for i in range(len(valid)):
            if rand[i] < tr_p[i]:
                points[valid[i]].set_infected(t, points[sourceid[valid[i]]], common_p)
                c += 1
        return c

    @staticmethod
    def get_transmission_p(beta, ds, infected_durations):
        # 0 - 1
        def distance_f(d):
            return np.exp(-d / 5)

        def duration_f(dt):
            return (np.tanh(dt-5)+0.2)*(np.tanh(-dt+8)+0.5)
            # return np.exp(-abs(np.random.normal(7, 2, len(dt)) - dt))

        dp = distance_f(ds)
        tp = duration_f(infected_durations)
        return beta * dp * tp