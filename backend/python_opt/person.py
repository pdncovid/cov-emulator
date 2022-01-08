import numpy as np

from backend.python_opt.enums import PersonFeatures, State, PersonOcc

n_characteristics = 3


def initialize_age(class_name):
    return int(np.random.rand() * 100)


def add_person(p, class_name, features=None):
    if features is not None:
        p[features[0]] = features
        return

    person = p[:, 0].max() + 1

    p[person, PersonFeatures.id.value] = person
    p[person, PersonFeatures.occ.value] = PersonOcc[class_name].value
    p[person, PersonFeatures.gender.value] = 0 if np.random.rand() < 0.5 else 1  # gender of the person
    p[person, PersonFeatures.age.value] = initialize_age(class_name)
    p[person, PersonFeatures.base_immunity.value] = 1 / p[person, 2] if np.random.rand() < 0.9 else np.random.rand()  # todo find
    p[person, PersonFeatures.immunity_boost.value] = 0
    p[person, PersonFeatures.behaviour.value] = 0.5  # behaviour of the point (healthy medical practices -> unhealthy)
    p[person, PersonFeatures.asymptotic_chance.value] = p[person, 3] ** 2
    p[person, PersonFeatures.is_asymptotic.value] = -1
    p[person, PersonFeatures.social_d.value] = 1
    p[person, PersonFeatures.hygiene_p.value] = 1
    p[person, PersonFeatures.temp.value] = 35
    p[person, PersonFeatures.state.value] = State.SUSCEPTIBLE.value
    p[person, PersonFeatures.disease_state.value] = 0
    p[person, PersonFeatures.source_id.value] = -1
    p[person, PersonFeatures.inf_t.value] = -1
    p[person, PersonFeatures.inf_l.value] = -1
    p[person, PersonFeatures.tested_t.value] = -1
    p[person, PersonFeatures.px.value] = -1
    p[person, PersonFeatures.py.value] = -1
    p[person, PersonFeatures.vx.value] = -1
    p[person, PersonFeatures.vy.value] = -1
    p[person, PersonFeatures.fr.value] = -1
    p[person, PersonFeatures.to.value] = -1
    p[person, PersonFeatures.tox.value] = -1
    p[person, PersonFeatures.toy.value] = -1
    p[person, PersonFeatures.cl_id.value] = -1
    p[person, PersonFeatures.cl_enter_t.value] = -1
    p[person, PersonFeatures.cl_leave_t.value] = -1
    p[person, PersonFeatures.cl_x.value] = -1
    p[person, PersonFeatures.cl_y.value] = -1
    p[person, PersonFeatures.cl_r.value] = -1
    p[person, PersonFeatures.cl_v_cap.value] = -1
    p[person, PersonFeatures.day_over.value] = 0
    p[person, PersonFeatures.home_id.value] = -1
    p[person, PersonFeatures.home_w_id.value] = -1
    p[person, PersonFeatures.work_id.value] = -1
    p[person, PersonFeatures.cm_id.value] = -1
    p[person, PersonFeatures.cm_enter_t.value] = -1
    p[person, PersonFeatures.fm_id.value] = -1
    p[person, PersonFeatures.is_transporter.value] = 0
    p[person, PersonFeatures.latched_id.value] = -1
