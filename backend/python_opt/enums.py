from enum import Enum

Mobility = Enum('Mobility', "RANDOM BROWNIAN")

PersonOcc = Enum('Person',
                 "SchoolBusDriver TuktukDriver Infant CommercialZoneBusDriver Student Teacher "
                 "CommercialWorker BusDriver GarmentWorker GarmentAdmin Retired")
PersonFeatures = Enum('Person Features',
                      "id occ gender age base_immunity immunity_boost behaviour asymptotic_chance is_asymptotic "
                      "social_d hygiene_p temp"
                      "state disease_state source_id inf_t inf_l tested_t"
                      "px py vx vy fr to tox toy "
                      "cl_id cl_enter_t cl_leave_t cl_x cl_y cl_r cl_v_cap "
                      "day_over home_id home_w_id work_id "
                      "cm_id cm_enter_t "
                      "fm_id "
                      "is_transporter latched_id "
                      "happiness social_class daily_income daily_expense")
# route character_vector

Location = Enum('Location',
                "Classroom GarmentWorkArea ResidentialPark EducationZone ResidentialZone GarmentOffice School "
                "DenseDistrict Home GatheringPlace SchoolCanteen UrbanBlock GarmentBuilding Hospital CommercialCanteen "
                "SparseDistrict CommercialBuilding GarmentCanteen Cemetery RuralBlock TukTukStation CommercialWorkArea "
                "CommercialZone MedicalZone COVIDQuarantineZone IndustrialZone BusStation")
State = Enum('State', "SUSCEPTIBLE INFECTED RECOVERED DEAD")
Shape = Enum('Shape', "POLYGON CIRCLE")
TestSpawn = Enum('Test center spawning method', 'RANDOM HEATMAP')
Containment = Enum('Containment strategy', "NONE LOCKDOWN QUARANTINE QUARANTINECENTER")
