# def enum(*sequential, **named):
#     enums = dict(zip(sequential, range(len(sequential))), **named)
#     return type('Enum', (), enums)

from enum import Enum

Mobility = Enum('Mobility', "RANDOM BROWNIAN")

State = Enum('State', "SUSCEPTIBLE INFECTED RECOVERED DEAD")
DiseaseState = Enum('DiseaseState', "INCUBATION INFECTIOUS MILD SEVERE CRITICAL")
Shape = Enum('Shape', "POLYGON CIRCLE")
TestSpawn = Enum('Test center spawning method', 'RANDOM HEATMAP')
Containment = Enum('Containment strategy', "NONE LOCKDOWN QUARANTINE QUARANTINECENTER ROSTER")
PersonFeatures = Enum('Person Features',
                      "id occ gender age base_immunity immunity_boost behaviour asymptotic_chance is_asymptotic "
                      "social_d hygiene_p temp "
                      "state disease_state infected_source_id infected_time infected_loc_id "
                      "tested_positive_time last_tested_time "
                      "px py vx vy fr to tox toy "
                      "cl_id cl_enter_t cl_leave_t cl_x cl_y cl_r cl_v_cap "
                      "home_id home_w_id work_id "
                      "cm_id cm_enter_t "
                      "fm_id "
                      "happiness base_happiness social_class daily_income economic_status ")
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
