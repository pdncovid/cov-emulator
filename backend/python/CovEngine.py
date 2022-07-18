import numpy as np
from scipy.stats import lognorm

from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.Logger import Logger
from backend.python.Time import Time
from backend.python.enums import *
from backend.python.functions import get_random_element


class Variant:
    def __init__(self, name, transmittable, severity):
        self.name = name
        self.transmittable = transmittable
        self.severity = severity


class CovEngine:
    variant_start_events = []
    current_variants = {}

    base_recovery_p = 0.8
    recover_after = Time.get_duration(24 * 21)
    die_after = Time.get_duration(24 * 14)

    dead_disease_state = len(DiseaseStates)
    daily_vaccinations = 10000
    immunity_boost_inc = 0.5
    redose_threshold = 0.5 * 0.8
    daily_immunity_boost_dec_factor = 0.95

    distributions = {'INCUBATION-INFECTIOUS': lognorm([1.5], loc=TransmissionEngine.incubation_days),
                     'INFECTIOUS-MILD': lognorm([0.9], loc=1.1), 'MILD-SEVERE': lognorm([4.9], loc=6.6),
                     'SEVERE-CRITICAL': lognorm([2], loc=1.5), 'CRITICAL-DEAD': lognorm([4.8], loc=10.7),
                     'MILD-RECOVERED': lognorm([2], loc=8), 'SEVERE-RECOVERED': lognorm([6.3], loc=18.1),
                     'CRITICAL-RECOVERED': lognorm([6.3], loc=18.1), 'ASYMPTOMATIC-RECOVERED': lognorm([2], loc=8),
                     'ASYMPTOMATIC-DEAD': lognorm([2], loc=8)}

    age_p = {'SEVERE': [0.0005, 0.00165, 0.0072, 0.0208, 0.0343, 0.0765, 0.1328, 0.20655, 0.2457, 0.2457],
             'CRITICAL': [0.00003, 0.00008, 0.00036, 0.00104, 0.00216, 0.00933, 0.03639, 0.08923, 0.1742, 0.1742],
             'DEAD': [0.00002, 0.00002, 0.0001, 0.00032, 0.00098, 0.00265, 0.00766, 0.02439, 0.08292, 0.08292]}

    @staticmethod
    def on_reset_day(day):
        for ve in CovEngine.variant_start_events:
            if int(ve['day']) <= day and ve["name"] not in CovEngine.current_variants:
                Logger.log(f"Added new COVID variant {ve['name']}", 'c')
                variant = Variant(ve["name"], float(ve["transmittable"]), float(ve["severity"]))
                CovEngine.current_variants[variant.name] = variant

    @staticmethod
    def get_infect_variant(p, source, name=None):  # todo add to doc
        if name is not None and name != "" and str(name) != "nan":
            return CovEngine.current_variants[name]
        if source == p:
            return get_random_element(list(CovEngine.current_variants.values()))
        if np.random.rand() < 0.5: #todo find this value
            return get_random_element(list(CovEngine.current_variants.values()))
        return source.infection_variant

    @staticmethod
    def vaccinate_people(l_age, u_age, people):
        unvaccinated = []
        for p in people:
            age = p.features[p.ID, PF_age]
            if p.features[p.ID, PF_immunity_boost] < CovEngine.redose_threshold and (
                    u_age >= age >= l_age):
                unvaccinated.append(p)

        np.random.shuffle(unvaccinated)

        for i, p in enumerate(unvaccinated):
            if i > CovEngine.daily_vaccinations:
                break
            p.features[p.ID, PF_immunity_boost] += CovEngine.immunity_boost_inc

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
                        if next_state == "RECOVERED":
                            p.set_recovered()
                        elif next_state == "DEAD":
                            p.set_dead()
                            Logger.log(f"DEAD {p.ID}", 'c')
                            cemetery[0].enter_person(p)
                        else:
                            next_state = DiseaseStates.index(next_state) + 1
                            p.set_disease_state(next_state, t)
                        break

                # if t - p.features[p.ID, PF_infected_time] > CovEngine.recover_after and \
                #         np.random.rand() < 0.1:  # todo find this value
                #     p.set_recovered()

    @staticmethod
    def next_disease_state(p, t):
        ds = p.features[p.ID, PF_disease_state]
        ps = []
        if p.features[p.ID, PF_is_asymptotic]==1:
            if ds == DiseaseState_INCUBATION:
                ps = ["INCUBATION-INFECTIOUS"]
            elif ds == DiseaseState_INFECTIOUS:
                ps = ['ASYMPTOMATIC-DEAD',
                      'ASYMPTOMATIC-RECOVERED']
        else:
            if ds == DiseaseState_INCUBATION:
                ps = ["INCUBATION-INFECTIOUS"]
            elif ds == DiseaseState_INFECTIOUS:
                ps = ["INFECTIOUS-MILD"]
            elif ds == DiseaseState_MILD:
                ps = ["MILD-SEVERE",
                      "MILD-RECOVERED"]
            elif ds == DiseaseState_SEVERE:
                ps = ["SEVERE-CRITICAL",
                      "SEVERE-RECOVERED"]
            elif ds == DiseaseState_CRITICAL:
                ps = ["CRITICAL-DEAD",
                      "CRITICAL-RECOVERED"]

        return ps

    @staticmethod
    def get_next_state_p(p, next_state):
        def age_f(a):
            if next_state in CovEngine.age_p.keys():
                return CovEngine.age_p[next_state][min(9, int(a // 10))]
            return (np.tanh((a - 60) / 20) + 1) / 2

        if len(next_state) == 0:
            return -1
        age_p = age_f(p.features[p.ID, PF_age])
        if next_state == "RECOVERED":  # get better probability
            p = CovEngine.base_recovery_p * p.get_effective_immunity() * age_p * (1-p.infection_variant.severity)
        else:  # worsen probability
            p = (1 - CovEngine.base_recovery_p) * (1 - p.get_effective_immunity()) * age_p * p.infection_variant.severity
        p = p ** (1 / 4)
        return p
