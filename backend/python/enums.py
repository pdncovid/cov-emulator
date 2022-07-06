# def enum(*sequential, **named):
#     enums = dict(zip(sequential, range(len(sequential))), **named)
#     return type('Enum', (), enums)
# i'm maama
from enum import Enum

Mobility = Enum('Mobility', "RANDOM BROWNIAN")

States = list("SUSCEPTIBLE INFECTED RECOVERED DEAD".split(' '))
State_SUSCEPTIBLE = 1
State_INFECTED = 2
State_RECOVERED = 3
State_DEAD = 4

DiseaseStates = list("INCUBATION INFECTIOUS MILD SEVERE CRITICAL".split(' '))
DiseaseState_INCUBATION = 1
DiseaseState_INFECTIOUS = 2
DiseaseState_MILD = 3
DiseaseState_SEVERE = 4
DiseaseState_CRITICAL = 5

Shapes = list("POLYGON CIRCLE".split(' '))
Shape_POLYGON = 1
Shape_CIRCLE = 2

TestSpawns = list('RANDOM HEATMAP'.split(' '))
TestSpawn_RANDOM = 1
TestSpawn_HEATMAP = 2

Containments = list("NONE LOCKDOWN QUARANTINE QUARANTINECENTER ROSTER".split(' '))
Containment_NONE = 1
Containment_LOCKDOWN = 2
Containment_QUARANTINE = 3
Containment_QUARANTINECENTER = 4
Containment_ROSTER = 5

PersonFeatures = ["id", "occ", "gender", "age", "base_immunity", "immunity_boost", "behaviour", "asymptotic_chance",
                  "is_asymptotic", "social_d", "hygiene_p", "temp", "state", "disease_state", "infected_source_id",
                  "infected_time", "infected_loc_id", "tested_positive_time", "last_tested_time", "px", "py", "vx",
                  "vy", "fr", "to", "tox", "toy", "cl_id", "cl_enter_t", "cl_leave_t", "cl_x", "cl_y", "cl_r",
                  "cl_v_cap", "home_id", "home_w_id", "work_id", "cm_id", "cm_enter_t", "fm_id", "happiness",
                  "base_happiness", "social_class", "daily_income", "economic_status"]
PF_id = 1
PF_occ = 2
PF_gender = 3
PF_age = 4
PF_base_immunity = 5
PF_immunity_boost = 6
PF_behaviour = 7
PF_asymptotic_chance = 8
PF_is_asymptotic = 9
PF_social_d = 10
PF_hygiene_p = 11
PF_temp = 12
PF_state = 13
PF_disease_state = 14
PF_infected_source_id = 15
PF_infected_time = 16
PF_infected_loc_id = 17
PF_tested_positive_time = 18
PF_last_tested_time = 19
PF_px = 20
PF_py = 21
PF_vx = 22
PF_vy = 23
PF_fr = 24
PF_to = 25
PF_tox = 26
PF_toy = 27
PF_cl_id = 28
PF_cl_enter_t = 29
PF_cl_leave_t = 30
PF_cl_x = 31
PF_cl_y = 32
PF_cl_r = 33
PF_cl_v_cap = 34
PF_home_id = 35
PF_home_w_id = 36
PF_work_id = 37
PF_cm_id = 38
PF_cm_enter_t = 39
PF_fm_id = 40
PF_happiness = 41
PF_base_happiness = 42
PF_social_class = 43
PF_daily_income = 44
PF_economic_status = 45


# LocationFeatures = Enum('Location features',
#                         "id loc px py shape depth ex ey parent_id capacity radius "
#                         "recovery_p infectious social_distance hygiene_boost quarantined quarantined_time "
#                         "om")
# PersonOcc = Enum('Person',
#                  "SchoolBusDriver TuktukDriver Infant CommercialZoneBusDriver Student Teacher "
#                  "CommercialWorker BusDriver GarmentWorker GarmentAdmin Retired")
class ClassNameMaps:
    lc_map = None
    pc_map = None
    mc_map = None
