import numpy as np
from tqdm import tqdm
import pandas as pd

from backend.python.Logger import Logger
from backend.python.enums import *
from backend.python.functions import bs
from backend.python.Time import Time


class TransmissionEngine:
    base_transmission_p = 0.1
    common_fever_p = 0.1
    override_social_dist = -1
    override_hygiene_p = -1

    incubation_days = 4.5

    p_hist = []

    @staticmethod
    def disease_transmission(points, r, analyze_infect_contacts_only, log_fine_details):

        from backend.python.point.Person import Person
        from backend.python.location.Location import Location
        Logger.df_detailed_person = pd.DataFrame(Logger.df_detailed_person)
        df = Logger.df_detailed_person[['person', 'x', 'y', 'current_location_id', 'time']]
        dfg = df.groupby('time')
        state = Person.features[:, PF_state]
        n_contacts = [0 for _ in range(len(state))]
        contacts = {i: [] for i in range(len(state))}
        new_infected = []
        for t in tqdm(dfg.groups.keys(), desc="Checking for virus transmission events"):
            dft = dfg.get_group(t)
            x = dft['x'].values
            y = dft['y'].values
            cur_loc_ids = dft['current_location_id'].values
            location_social_dist = np.array([Location.all_locations[lid].social_distance for lid in cur_loc_ids])
            social_dist = location_social_dist
            if TransmissionEngine.override_social_dist > -1:
                social_dist = social_dist * 0 + TransmissionEngine.override_social_dist

            _n_contacts, _contacts, distance, sourceid = TransmissionEngine.get_close_contacts_and_distance(
                x, y, state, social_dist, r, analyze_infect_contacts_only)

            if log_fine_details:
                Logger.update_person_contact_log(points, _n_contacts, _contacts, t)

            new_infected += TransmissionEngine.transmit_disease(points, cur_loc_ids, _n_contacts, _contacts, distance,
                                                                sourceid, t // Time._scale)  # TODO CHECK _SCALE

            for i in range(len(state)):
                n_contacts[i] += _n_contacts[i]
                contacts[i] += _contacts[i]

        return np.array(n_contacts), contacts, np.array(new_infected)

    @staticmethod
    # @njit
    def get_close_contacts_and_distance(x, y, state, social_dist, r, analyze_infect_contacts_only):

        from backend.python.point.Person import Person

        contacts = {i: [] for i in range(len(x))}
        n_contacts = np.zeros(len(x), dtype=np.int64)
        distance = np.ones(len(x)) * 1000
        sourceid = np.ones(len(x), dtype=np.int64) * -1

        xs_idx = np.argsort(x)
        ys_idx = np.argsort(y)
        xs = x[xs_idx]
        ys = y[ys_idx]

        if analyze_infect_contacts_only:
            _range = np.where(state == State_INFECTED)[0]
        else:
            _range = range(len(x))
        for i in _range:
            x_idx_r = bs(xs, x[i] + r)
            x_idx_l = bs(xs, x[i] - r)

            y_idx_r = bs(ys, y[i] + r)
            y_idx_l = bs(ys, y[i] - r)

            close_points_idx = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r], assume_unique=True)
            self_contact_idx = np.where(close_points_idx == i)[0]
            close_points_idx = np.delete(close_points_idx, self_contact_idx)

            d = np.sqrt(np.power(x[close_points_idx] - x[i], 2) + np.power(y[close_points_idx] - y[i], 2))

            # select_from_close = np.logical_and(d < r, d > social_dist[close_points_idx])
            d = np.maximum(d, social_dist[close_points_idx])
            select_from_close = d < r
            d = d[select_from_close]
            close_points_idx = close_points_idx[select_from_close]

            # add contacts to dictionary
            for ci in close_points_idx:
                contacts[ci].append(i)
                contacts[i].append(ci)

            n_contacts[close_points_idx] += 1
            n_contacts[i] += len(close_points_idx)

            if state[i] == State_INFECTED: #and (Person.features[i, PF_disease_state] != DiseaseState_INCUBATION or
                                          #     Person.features[i, PF_disease_state] != DiseaseState_MILD):
                # select_from_sus = np.logical_or(state[close_points_idx] == State_SUSCEPTIBLE, state[close_points_idx] == State_RECOVERED) # TODO add reinfect different variant
                select_from_sus = state[close_points_idx] == State_SUSCEPTIBLE
                close_points_idx = close_points_idx[select_from_sus]
                d = d[select_from_sus]
                sourceid[close_points_idx[d < distance[close_points_idx]]] = i
                distance[close_points_idx] = np.minimum(d + 1e-6, distance[close_points_idx])

        return n_contacts, contacts, distance, sourceid

    @staticmethod
    def transmit_disease(points, cur_loc_ids, n_contacts, contacts, distance, sourceid, t):

        from backend.python.point.Person import Person
        from backend.python.location.Location import Location

        valid = np.where(sourceid > -1)[0]
        validsourceid = sourceid[valid]

        age = Person.features[validsourceid, PF_age]
        # age = np.array(age)

        infected_duration = []
        for i in validsourceid:
            infected_duration.append(t - points[i].features[points[i].ID, PF_infected_time])
        infected_duration = np.array(infected_duration)

        tr_p = TransmissionEngine.get_transmission_p(distance[valid], n_contacts[valid], age, infected_duration)

        # add 0.3 to avoid random infections
        rand = np.random.rand(len(valid))  # + 0.3

        c = []
        for i in range(len(valid)):
            contact_person = points[valid[i]]
            infected_person = points[sourceid[valid[i]]]
            contact_person_cur_loc = Location.all_locations[cur_loc_ids[contact_person.ID]]
            # infected_person_cur_loc = Location.all_locations[cur_loc_ids[infected_person.ID]]

            location_p = contact_person_cur_loc.infectious
            trans_p = TransmissionEngine.get_transport_transmission_p(contact_person, infected_person)
            variant_p = infected_person.infection_variant.transmittable
            immunity_p = (1 - contact_person.get_effective_immunity()) * (1 - infected_person.get_effective_immunity())
            hygiene_p = Person.features[contact_person.ID, PF_hygiene_p] * \
                        Person.features[infected_person.ID, PF_hygiene_p]
            asym_p = .25 if infected_person.features[infected_person.ID, PF_is_asymptotic] == 1 else 1
            if TransmissionEngine.override_hygiene_p > 0:
                hygiene_p = TransmissionEngine.override_hygiene_p

            p = ((tr_p[i] * trans_p * location_p * hygiene_p * immunity_p * variant_p) ** (2.6 / 1)) * asym_p
            TransmissionEngine.p_hist.append(
                (p, tr_p[i], trans_p, location_p, hygiene_p, immunity_p, variant_p, asym_p))
            if rand[i] < p:
                contact_person.set_infected(t, infected_person, contact_person_cur_loc,
                                            TransmissionEngine.common_fever_p)
                c.append(contact_person.ID)
        return c

    @staticmethod
    def get_transmission_p(ds, n_contacts, age, infected_duration):
        # 0 - 1
        def distance_f(d):
            return np.exp(-d / 5)

        def duration_f(dt):
            dt = np.array(list(map(Time.i_to_minutes, dt)))
            x = dt / 60 / 24
            mu = 0
            sig = 10
            p = np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
            return p

        def count_f(c):
            c[c > 5] = 10
            return (c + (1 - (c / 20 + 0.5)) ** 2) / 5

        # def age_f(a):
        #     return (np.tanh((a - 60) / 20) + 2) / 3

        dp = distance_f(ds)
        tp = duration_f(infected_duration)
        cp = count_f(n_contacts)
        # ap = age_f(age)
        return (TransmissionEngine.base_transmission_p * dp * cp * tp) **(1/4)  # todo check 1/4

    @staticmethod
    def get_transport_transmission_p(p1, p2):
        if p1.current_trans != p1.current_trans:
            return 0
        if p1.all_movement_ids[p1.ID] != p2.all_movement_ids[p2.ID]:  # not in same movement
            return 0
        if p1.latched_to != p2.latched_to:
            return 0
        # todo implement infection within latched people only! (in MovementByTransporter)

        return p1.current_trans.infectiousness
