import numpy as np

from backend.python.Logger import Logger
from backend.python.Time import Time


class CovEngine:
    base_recovery_p = 0.8
    recover_after = Time.get_duration(24 * 21)
    dead_disease_state = 5
    daily_vaccinations = 10000
    immunity_boost_inc = 0.5
    redose_threshold = 0.5*0.8
    daily_immunity_boost_dec_factor = 0.95

    @staticmethod
    def vaccinate_people(l_age, u_age, people):
        unvaccinated = []
        for p in people:
            if p.immunity_boost < CovEngine.redose_threshold and (u_age >= p.age >= l_age):
                unvaccinated.append(p)

        np.random.shuffle(unvaccinated)

        for i, p in enumerate(unvaccinated):
            if i>CovEngine.daily_vaccinations:
                break
            p.immunity_boost += CovEngine.immunity_boost_inc



    @staticmethod
    def process_recovery(points, t):
        for i, p in enumerate(points):
            if p.is_infected():
                if p.is_asymptotic:
                    if np.random.rand() < CovEngine.get_recovery_p(p, t):
                        p.set_recovered()
                else:
                    if np.random.rand() < CovEngine.get_recovery_p(p, t):
                        p.disease_state -= 1
                        if p.disease_state == 0:
                            p.set_recovered()

    @staticmethod
    def process_death(points, t, cemetery):
        for i, p in enumerate(points):
            if p.is_infected():
                if p.is_asymptotic:
                    if np.random.rand() < CovEngine.get_worsen_p(p, t):
                        p.set_dead()
                else:
                    if np.random.rand() < CovEngine.get_worsen_p(p, t):
                        p.disease_state += 1
                        if p.disease_state == CovEngine.dead_disease_state:
                            p.set_dead()

                if t - p.infected_time > CovEngine.recover_after and np.random.rand() < 0.5:  # todo find this value
                    p.set_recovered()
                if p.is_dead():
                    Logger.log(f"DEAD {p.ID}", 'c')
                    cemetery[0].enter_person(p)

    @staticmethod
    def get_recovery_p(p, t):
        # 0 - 1
        def duration_f(dt):
            return ((np.tanh((dt - Time.get_duration(24 * 14)) / Time.get_duration(24 * 14)) + 0.2) *
                    (np.tanh(
                        (-dt + Time.get_duration(24 * 20)) / Time.get_duration(24 * 20)) + 0.5) + 1.19987) / 2.6683940
            # return np.exp(-abs(np.random.normal(7, 2, len(dt)) - dt))

        lp = p.get_current_location().recovery_p
        tp = duration_f(t - p.infected_time)
        return CovEngine.base_recovery_p * tp * lp * p.get_effective_immunity()

    @staticmethod
    def get_worsen_p(p, t):
        # 0 - 1
        def duration_f(dt):
            return ((np.tanh((dt - Time.get_duration(24 * 14)) / Time.get_duration(24 * 14)) + 0.2) *
                    (np.tanh(
                        (-dt + Time.get_duration(24 * 20)) / Time.get_duration(24 * 20)) + 0.5) + 1.19987) / 2.6683940
            # return np.exp(-abs(np.random.normal(7, 2, len(dt)) - dt))

        lp = p.get_current_location().recovery_p
        tp = duration_f(t - p.infected_time)
        return (1 - CovEngine.base_recovery_p) * tp * (1 - lp) * (1 - p.get_effective_immunity()) * 0.1


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    dt = np.linspace(0, Time.get_duration(24 * 60), 100000)
    plt.plot(dt, ((np.tanh((dt - Time.get_duration(24 * 14)) / Time.get_duration(24 * 14)) + 0.2) *
                  (np.tanh(
                      (-dt + Time.get_duration(24 * 20)) / Time.get_duration(24 * 20)) + 0.5) + 1.19987) / 2.6683940)
    plt.show()
