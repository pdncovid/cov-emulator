import numpy as np
from tqdm import tqdm

from backend.python.Logger import Logger
from backend.python.enums import State, PersonFeatures, DiseaseState
from backend.python.functions import bs
from backend.python.Time import Time

from backend.python.point.Person import Person
from backend.python.location.Location import Location

class TransmissionEngine:
    base_transmission_p = 0.1
    common_fever_p = 0.1
    override_social_dist = -1
    override_hygiene_p = -1

    incubation_days = 4.5

    @staticmethod
    def disease_transmission(points, t, r):
        df = Logger.df_detailed_person[['person', 'x', 'y', 'current_location_id', 'time']]
        dfg = df.groupby('time')
        state = Person.features[:, PersonFeatures.state.value]
        person_social_dist = Person.features[:, PersonFeatures.social_d.value]
        n_contacts = [0 for _ in range(len(state))]
        contacts = {i: [] for i in range(len(state))}
        new_infected = []
        for t in tqdm(dfg.groups.keys(), desc="Checking for virus transmission events"):
            dft = dfg.get_group(t)
            x = dft['x'].values
            y = dft['y'].values
            cur_loc_ids = dft['current_location_id'].values
            location_social_dist = np.array([Location.all_locations[lid].social_distance for lid in cur_loc_ids])
            social_dist = np.maximum(person_social_dist, location_social_dist)
            if TransmissionEngine.override_social_dist > -1:
                social_dist = social_dist*0 + TransmissionEngine.override_social_dist

            _n_contacts, _contacts, distance, sourceid = TransmissionEngine.get_close_contacts_and_distance(
                x, y, state, social_dist, r)
            Logger.update_person_contact_log(points, _n_contacts, _contacts, t)

            new_infected += TransmissionEngine.transmit_disease(points, cur_loc_ids, _n_contacts, _contacts, distance, sourceid, t//Time._scale)

            for i in range(len(state)):
                n_contacts[i] += _n_contacts[i]
                contacts[i] += _contacts[i]

        return np.array(n_contacts), contacts, np.array(new_infected)

        # x = Person.features[:, PersonFeatures.px.value]
        # y = Person.features[:, PersonFeatures.py.value]
        # state = Person.features[:, PersonFeatures.state.value]
        # person_social_dist = Person.features[:, PersonFeatures.social_d.value]
        # location_social_dist = np.array([p.get_current_location().social_distance for p in points])
        # social_dist = np.maximum(person_social_dist, location_social_dist)
        # n_contacts, contacts, distance, sourceid = TransmissionEngine. \
        #     get_close_contacts_and_distance(x, y, state, social_dist, r)
        #
        # new_infected = TransmissionEngine.transmit_disease(points, n_contacts, contacts, distance, sourceid, t)
        #
        # return n_contacts, contacts, new_infected

    @staticmethod
    # @njit
    def get_close_contacts_and_distance(x, y, state, social_dist, r):
        contacts = {i: [] for i in range(len(x))}
        n_contacts = np.zeros(len(x), dtype=np.int64)
        distance = np.ones(len(x)) * 1000
        sourceid = np.ones(len(x), dtype=np.int64) * -1

        xs_idx = np.argsort(x)
        ys_idx = np.argsort(y)
        xs = x[xs_idx]
        ys = y[ys_idx]

        processed = 0
        # for i in np.where(state == State.INFECTED.value)[0]:
        for i in range(len(x)):
            x_idx_r = bs(xs, x[i] + r)
            x_idx_l = bs(xs, x[i] - r)

            y_idx_r = bs(ys, y[i] + r)
            y_idx_l = bs(ys, y[i] - r)

            close_points_idx = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r], assume_unique=True)
            processed += len(close_points_idx)

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

            if state[i] == State.INFECTED.value and Person.features[i, PersonFeatures.disease_state.value] != DiseaseState.INCUBATION.value:
                select_from_sus = state[close_points_idx] == State.SUSCEPTIBLE.value
                close_points_idx = close_points_idx[select_from_sus]
                d = d[select_from_sus]
                sourceid[close_points_idx[d < distance[close_points_idx]]] = i
                distance[close_points_idx] = np.minimum(d + 1e-6, distance[close_points_idx])

        return n_contacts, contacts, distance, sourceid

    @staticmethod
    def transmit_disease(points, cur_loc_ids, n_contacts, contacts, distance, sourceid, t):
        valid = np.where(sourceid > -1)[0]
        validsourceid = sourceid[valid]
        infected_duration = []
        age = Person.features[validsourceid, PersonFeatures.age.value]
        for i in validsourceid:
            infected_duration.append(t - points[i].features[points[i].ID, PersonFeatures.infected_time.value])

        infected_duration = np.array(infected_duration)
        age = np.array(age)
        tr_p = TransmissionEngine.get_transmission_p(distance[valid],  n_contacts[valid], infected_duration,age)

        # add 0.3 to avoid random infections
        rand = np.random.rand(len(valid)) #+ 0.3

        c = []
        for i in range(len(valid)):
            contact_person = points[valid[i]]
            infected_person = points[sourceid[valid[i]]]
            contact_person_cur_loc = Location.all_locations[cur_loc_ids[contact_person.ID]]
            # infected_person_cur_loc = Location.all_locations[cur_loc_ids[infected_person.ID]]

            location_p = contact_person_cur_loc.infectious
            hygiene_p = Person.features[contact_person.ID, PersonFeatures.hygiene_p.value] * \
                          Person.features[infected_person.ID, PersonFeatures.hygiene_p.value]
            if TransmissionEngine.override_hygiene_p > -1:
                hygiene_p = TransmissionEngine.override_hygiene_p
            immunity_p = (1 - contact_person.get_effective_immunity()) * (1 - infected_person.get_effective_immunity())
            trans_p = TransmissionEngine.get_transport_transmission_p(contact_person, infected_person)

            if rand[i] < tr_p[i] * trans_p * location_p * hygiene_p * immunity_p:
                contact_person.set_infected(t, infected_person, contact_person_cur_loc,TransmissionEngine.common_fever_p)
                c.append(contact_person.ID)
        return c

    @staticmethod
    def get_transmission_p(ds, n_contacts, infected_durations, age):
        # 0 - 1
        def distance_f(d):
            return np.exp(-d / 5)

        def duration_f(dt):
            dt = np.array(list(map(Time.i_to_minutes, dt)))
            x = dt / 60 / 24
            mu = 15
            sig = 10
            p = np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
            # p[x<TransmissionEngine.incubation_days] = 0
            return p

        def count_f(c):
            c[c > 5] = 10
            return (c + (1 - (c / 20 + 0.5)) ** 2) / 5

        def age_f(a):
            return (np.tanh((a - 60) / 20) + 2) / 3

        dp = distance_f(ds)
        tp = duration_f(infected_durations)
        cp = count_f(n_contacts)
        ap = age_f(age)
        return TransmissionEngine.base_transmission_p * dp * tp * cp * ap

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
