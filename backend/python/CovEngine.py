import numpy as np
from scipy.stats import lognorm

from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.Logger import Logger
from backend.python.Time import Time
from backend.python.enums import PersonFeatures, DiseaseState, State


class CovEngine:
    base_recovery_p = 0.8
    recover_after = Time.get_duration(24 * 21)
    die_after = Time.get_duration(24 * 14)

    dead_disease_state = len(DiseaseState)
    daily_vaccinations = 10000
    immunity_boost_inc = 0.5
    redose_threshold = 0.5 * 0.8
    daily_immunity_boost_dec_factor = 0.95

    distributions = {}
    distributions['INCUBATION-INFECTIOUS'] = lognorm([1.5], loc=TransmissionEngine.incubation_days)
    distributions['INFECTIOUS-MILD'] = lognorm([0.9], loc=1.1)
    distributions['MILD-SEVERE'] = lognorm([4.9], loc=6.6)
    distributions['SEVERE-CRITICAL'] = lognorm([2], loc=1.5)
    distributions['CRITICAL-DEAD'] = lognorm([4.8], loc=10.7)

    distributions['MILD-RECOVERED'] = lognorm([2], loc=8)
    distributions['SEVERE-RECOVERED'] = lognorm([6.3], loc=18.1)
    distributions['CRITICAL-RECOVERED'] = lognorm([6.3], loc=18.1)

    distributions['ASYMPTOMATIC-RECOVERED'] = lognorm([2], loc=8)
    distributions['ASYMPTOMATIC-DEAD'] = lognorm([2], loc=8)  # TODO find this

    age_p = {'SEVERE': [0.0005, 0.00165, 0.0072, 0.0208, 0.0343, 0.0765, 0.1328, 0.20655, 0.2457, 0.2457],
             'CRITICAL': [0.00003, 0.00008, 0.00036, 0.00104, 0.00216, 0.00933, 0.03639, 0.08923, 0.1742, 0.1742],
             'DEAD': [0.00002, 0.00002, 0.0001, 0.00032, 0.00098, 0.00265, 0.00766, 0.02439, 0.08292, 0.08292]}

    @staticmethod
    def vaccinate_people(l_age, u_age, people):
        unvaccinated = []
        for p in people:
            age = p.features[p.ID, PersonFeatures.age.value]
            if p.features[p.ID, PersonFeatures.immunity_boost.value] < CovEngine.redose_threshold and (
                    u_age >= age >= l_age):
                unvaccinated.append(p)

        np.random.shuffle(unvaccinated)

        for i, p in enumerate(unvaccinated):
            if i > CovEngine.daily_vaccinations:
                break
            p.features[p.ID, PersonFeatures.immunity_boost.value] += CovEngine.immunity_boost_inc

    @staticmethod
    def process_disease_state(points, t, cemetery):
        for i, p in enumerate(points):
            if p.is_infected():
                possible_states = CovEngine.next_disease_state(p, t)
                dt = (t - p.disease_state_set_time) / Time.DAY
                for ps in possible_states:
                    next_state = ps.split('-')[1]
                    if np.random.rand() < CovEngine.get_next_state_p(p, next_state) * CovEngine.distributions[ps].cdf(
                            dt):
                        if next_state == State.RECOVERED.name:
                            p.set_recovered()
                        elif next_state == State.DEAD.name:
                            p.set_dead()
                            Logger.log(f"DEAD {p.ID}", 'c')
                            cemetery[0].enter_person(p)
                        else:
                            p.set_disease_state(next_state, t)
                        break

                # if t - p.features[p.ID, PersonFeatures.infected_time.value] > CovEngine.recover_after and \
                #         np.random.rand() < 0.1:  # todo find this value
                #     p.set_recovered()

        # for i, p in enumerate(points):
        #     if p.is_infected():
        #         if p.features[p.ID, PersonFeatures.is_asymptotic.value]:
        #             if np.random.rand() < CovEngine.get_recovery_p(p, t):
        #                 p.set_recovered()
        #             if np.random.rand() < CovEngine.get_worsen_p(p, t):
        #                 p.set_dead()
        #         else:
        #             if np.random.rand() < CovEngine.get_recovery_p(p, t):
        #                 p.features[p.ID, PersonFeatures.disease_state.value] -= 1
        #                 if p.features[p.ID, PersonFeatures.disease_state.value] == 0:
        #                     p.set_recovered()
        #             if np.random.rand() < CovEngine.get_worsen_p(p, t):
        #                 p.features[p.ID, PersonFeatures.disease_state.value] += 1
        #                 if p.features[p.ID, PersonFeatures.disease_state.value] == CovEngine.dead_disease_state:
        #                     p.set_dead()
        #         if t - p.features[
        #             p.ID, PersonFeatures.infected_time.value] > CovEngine.recover_after and np.random.rand() < 0.1:  # todo find this value
        #             p.set_recovered()
        #         if p.is_dead():
        #             Logger.log(f"DEAD {p.ID}", 'c')
        #             cemetery[0].enter_person(p)

    @staticmethod
    def next_disease_state(p, t):
        ds = p.features[p.ID, PersonFeatures.disease_state.value]
        ps = []
        if p.features[p.ID, PersonFeatures.is_asymptotic.value]:
            if ds == DiseaseState.INCUBATION.value:
                ps = [DiseaseState.INCUBATION.name + '-' + DiseaseState.INFECTIOUS.name]
            elif ds == DiseaseState.INFECTIOUS.value:
                ps = ['ASYMPTOMATIC-' + State.DEAD.name,
                      'ASYMPTOMATIC-' + State.RECOVERED.name]
        else:
            if ds == DiseaseState.INCUBATION.value:
                ps = [DiseaseState.INCUBATION.name + '-' + DiseaseState.INFECTIOUS.name]
            elif ds == DiseaseState.INFECTIOUS.value:
                ps = [DiseaseState.INFECTIOUS.name + '-' + DiseaseState.MILD.name]
            elif ds == DiseaseState.MILD.value:
                ps = [DiseaseState.MILD.name + '-' + DiseaseState.SEVERE.name,
                      DiseaseState.MILD.name + '-' + State.RECOVERED.name]
            elif ds == DiseaseState.SEVERE.value:
                ps = [DiseaseState.SEVERE.name + '-' + DiseaseState.CRITICAL.name,
                      DiseaseState.SEVERE.name + '-' + State.RECOVERED.name]
            elif ds == DiseaseState.CRITICAL.value:
                ps = [DiseaseState.CRITICAL.name + '-' + State.DEAD.name,
                      DiseaseState.CRITICAL.name + '-' + State.RECOVERED.name]

        return ps

    @staticmethod
    def get_next_state_p(p, next_state):
        def age_f(a):
            if next_state in CovEngine.age_p.keys():
                return CovEngine.age_p[next_state][min(9, int(a // 10))]
            return (np.tanh((a - 60) / 20) + 1) / 2

        if len(next_state) == 0:
            return -1
        age_p = age_f(p.features[p.ID, PersonFeatures.age.value])
        if next_state == State.RECOVERED.name:  # get better probability
            p = CovEngine.base_recovery_p * p.get_effective_immunity() * age_p
        else:  # worsen probability
            p = (1 - CovEngine.base_recovery_p) * (1 - p.get_effective_immunity()) * age_p
        p = p ** (1 / 3)
        return p

    # @staticmethod
    # def get_recovery_p(p, t):
    #     # 0 - 1
    #     def duration_f(dt):
    #         mu = 15
    #         sig = 5
    #         x = dt / 60 / 24
    #         return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
    #         # return np.exp(-abs(np.random.normal(7, 2, len(dt)) - dt))
    #
    #     infected_time = p.features[p.ID, PersonFeatures.infected_time.value]
    #     lp = p.get_current_location().recovery_p
    #     tp = duration_f(t - infected_time)
    #     if t - infected_time < CovEngine.recover_after and p.features[p.ID, PersonFeatures.disease_state.value] == 0:
    #         # too early to recover
    #         return 0
    #     return CovEngine.base_recovery_p * tp * lp * p.get_effective_immunity()
    #
    # @staticmethod
    # def get_worsen_p(p, t):
    #     # 0 - 1
    #
    #     def duration_f(dt):
    #         dt = Time.i_to_minutes(dt)
    #         mu = 15
    #         sig = 10
    #         x = dt / 60 / 24
    #         return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
    #         # return np.exp(-abs(np.random.normal(7, 2, len(dt)) - dt))
    #
    #     def age_f(a):
    #         return (np.tanh((a - 60) / 20) + 1) / 2
    #
    #     infected_time = p.features[p.ID, PersonFeatures.infected_time.value]
    #     lp = p.get_current_location().recovery_p
    #     tp = duration_f(t - infected_time)
    #     ageP = age_f(p.features[p.ID, PersonFeatures.age.value])
    #     if t - infected_time < CovEngine.die_after and p.features[
    #         p.ID, PersonFeatures.disease_state.value] == CovEngine.dead_disease_state - 1:
    #         # too early to die
    #         return 0
    #     wp = (1 - CovEngine.base_recovery_p) * tp * ageP * (1 - lp) * (1 - p.get_effective_immunity())
    #     wp = wp ** (1 / 1)
    #     # print(wp, (1 - CovEngine.base_recovery_p) , tp ,t, infected_time, t - infected_time, ageP , (1 - lp) , (1 - p.get_effective_immunity()))
    #     return wp
