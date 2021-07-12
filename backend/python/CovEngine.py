import numpy as np

from backend.python.Logger import Logger
from backend.python.Time import  Time


class CovEngine:
    base_recovery_p = 0.8
    death_after = Time.get_duration(24*21)
    dead_disease_state = 5

    @staticmethod
    def process_recovery(points, t):
        for i, p in enumerate(points):
            if p.is_infected():
                if np.random.rand() < CovEngine.get_recovery_p(p, t):
                    p.disease_state -= 1
                    if p.disease_state == 0:
                        p.set_recovered()

    @staticmethod
    def process_death(points, t, cemetery):
        for i, p in enumerate(points):
            if p.is_infected():
                if np.random.rand() < CovEngine.get_worsen_p(p, t):
                    p.disease_state += 1
                    if p.disease_state == CovEngine.dead_disease_state:
                        p.set_dead()

                if t - p.infected_time > CovEngine.death_after and np.random.rand() < 0.5: # todo find this value
                    p.set_dead()
                if p.is_dead():
                    Logger.log(f"DEAD {p.ID}", 'c')
                    cemetery[0].enter_person(p)

    @staticmethod
    def get_recovery_p(p, t):
        # 0 - 1
        def duration_f(dt):
            return ((np.tanh((dt - Time.get_duration(24 * 5)) / Time.get_duration(24 * 5)) + 0.2) *
                    (np.tanh((-dt + Time.get_duration(24 * 8)) / Time.get_duration(24 * 8)) + 0.5) + 1.19987) / 2.6683940
            # return np.exp(-abs(np.random.normal(7, 2, len(dt)) - dt))

        lp = p.get_current_location().recovery_p
        tp = duration_f(t - p.infected_time)
        return CovEngine.base_recovery_p * tp * lp*p.immunity

    @staticmethod
    def get_worsen_p(p, t):
        # 0 - 1
        def duration_f(dt):
            return ((np.tanh((dt - Time.get_duration(24 * 14)) / Time.get_duration(24 * 14)) + 0.2) *
                    (np.tanh((-dt + Time.get_duration(24 * 20)) / Time.get_duration(24 * 20)) + 0.5) + 1.19987) / 2.6683940
            # return np.exp(-abs(np.random.normal(7, 2, len(dt)) - dt))

        lp = p.get_current_location().recovery_p
        tp = duration_f(t - p.infected_time)
        return (1-CovEngine.base_recovery_p) * tp * (1-lp)*(1-p.immunity)*0.1


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    dt = np.linspace(0, Time.get_duration(24 * 60), 100000)
    plt.plot(dt, ((np.tanh((dt - Time.get_duration(24 * 14)) / Time.get_duration(24 * 14)) + 0.2) *
                    (np.tanh((-dt + Time.get_duration(24 * 20)) / Time.get_duration(24 * 20)) + 0.5) + 1.19987) / 2.6683940)
    plt.show()
