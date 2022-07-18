import argparse
import json
import os
import time

import numpy as np
from tqdm import tqdm

from backend.python.CharacterEngine import CharacterEngine
from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.CovEngine import CovEngine
from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.TestingEngine import TestingEngine
from backend.python.Time import Time
from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.enums import *
from backend.python.functions import count_graph_n, separate_into_classes
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Location import Location
from backend.python.location.TestCenter import TestCenter
from backend.python.point.Person import Person
from backend.python.point.Transporter import Transporter
from backend.python.transport.Movement import Movement

# ====================================== PARAMETERS =====================================================
testing_freq = 10
test_center_spawn_check_freq = 10
test_center_spawn_method = TestSpawn_HEATMAP
test_center_spawn_threshold = 100



def set_parameters(args):
    Logger('logs', time.strftime(args.name + '%Y.%m.%d-%H.%M.%S', time.localtime()), print=True, write=False)
    os.makedirs('../../app/src/data/' + Logger.test_name)
    # ========================================================================================== save initial parameters
    loc_classes = Location.class_df['l_class']
    people_classes = Person.class_df['p_class']
    movement_classes = Movement.class_df['m_class']
    lc_map = {x: i for i, x in enumerate(loc_classes)}
    pc_map = {x: i for i, x in enumerate(people_classes)}
    mc_map = {x: i for i, x in enumerate(movement_classes)}
    lc_map[None], pc_map[None], mc_map[None], = -1, -1, -1
    ClassNameMaps.lc_map = lc_map
    ClassNameMaps.pc_map = pc_map
    ClassNameMaps.mc_map = mc_map
    # save_array("../../app/src/data/locs.txt", loc_classes)
    # save_array("../../app/src/data/people.txt", people_classes)

    TransmissionEngine.override_social_dist = float(args.social_distance)
    TransmissionEngine.override_hygiene_p = float(args.hygiene_p)
    if TransmissionEngine.override_hygiene_p == 0:
        raise Exception("Always hygienic! no infection will occur!")

    TransmissionEngine.base_transmission_p = float(args.base_transmission_p)
    TransmissionEngine.incubation_days = float(args.incubation_days)

    # initialize variants
    added_variant_events = json.loads(args.addedVariantEvents)
    CovEngine.variant_start_events = [added_variant_events[key] for key in added_variant_events.keys()]
    print(CovEngine.variant_start_events)
    CovEngine.on_reset_day(0)

    # initialize simulator timer
    Time.init()

    # initialize route planner
    RoutePlanningEngine.set_parameters((Time.get_time() // Time.DAY) % 7)


# ==================================== END PARAMETERS ====================================================


def update_point_parameters(args):
    for p in Person.all_people:
        p.update_temp(args.common_fever_p)


def get_instance(people):
    x = Person.features[:, PF_px]
    y = Person.features[:, PF_py]
    ploc_ids = [p.get_current_location().ID for p in people]
    return x, y, ploc_ids


def executeSim(people, root, containment_events, gather_events, vaccinate_events, args):
    integrity_test = False
    log_fine_details = args.log_fine_details == 1
    analyze_infect_contacts_only = args.analyze_infect_contacts_only == 1
    is_loading = args.load_log_name != 'NONE'

    # process_disease_freq = 1  # Time.get_duration(2)
    # process_disease_at = process_disease_freq
    days = args.sim_days
    if is_loading:
        start_day = int(args.load_log_day)
    else:
        start_day = 0
    iterations = int(days * 1440 / Time._scale)
    n_overtime = 0
    Logger.save_class_info()
    Logger.save_args(args)

    # initialize graphs and people
    locations = root.get_locations_according_function(lambda x: True)

    # ============================================================================================== check house density
    loc_classes = separate_into_classes(root)
    for loc_class in loc_classes.keys():
        if 'Home' == loc_class:
            print(loc_class, len(loc_classes[loc_class]))
            pph = len(people) / len(loc_classes[loc_class])
            if pph > 4.5:
                Logger.log(
                    f'Houses are too dense with people. Increase houses or reduce population. People per house is {pph}',
                    'c')
                exit(-1)

    # ================================================================================ add test centers to medical zones
    test_centers = []
    if args.testing_strategy == "HOSPITAL":
        if 'MedicalZone' in loc_classes.keys():
            for mz in loc_classes['MedicalZone']:
                test_center = TestCenter(mz.px, mz.py, args.r_test_centers)
                test_centers.append(test_center)

    # ================================================================================================== find cemeteries
    cemetery = loc_classes['Cemetery']

    # ========================================================= initial iterations to initialize positions of the people
    if not is_loading:
        for t in range(5):
            print(f"initializing {t}")
            MovementEngine.move_people(Person.all_people)

    Logger.log(f"{len(people)} {count_graph_n(root)}", 'c')

    # ============================================================================================== main iteration loop
    day_t_instances = []
    new_infected = []
    elapsed_time = time.time()
    for iteration in range(iterations):
        t = Time.get_time()
        day = int(t // Time.DAY)

        print(f"\r=========================Iteration: {t} {Time.i_to_time(t)}====================== nOT={n_overtime}",
              end='')

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! reset day !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if t % Time.DAY == 0:
            day_t_instances = np.array(day_t_instances)

            # set today's containment strategy
            ces = []
            for ce in containment_events.keys():
                ces.append(containment_events[ce])
            ces.sort(key=lambda x: int(x["startday"]))

            # update covid engine parameters
            CovEngine.on_reset_day(day)

            for ce in ces:
                if int(ce["startday"]) == day:
                    ContainmentEngine.current_strategy = ce["containment_strategy"]
                    Logger.log(f"Containment strategy changed to {ContainmentEngine.current_strategy}", 'c')
                    if ce["containment_strategy"] == "ROSTER":
                        ContainmentEngine.assign_roster_days(people, int(ce["roster_groups"]))
                    else:
                        ContainmentEngine.current_rosters = 1


            if iteration > 0:
                # ================================================================================= process transmission
                n_con, contacts, new_infected = TransmissionEngine.disease_transmission(people, args.inf_radius, analyze_infect_contacts_only, log_fine_details)
                # Logger.log(f"{len(new_infected)}/{sum(n_con > 0)}/{int(sum(n_con))} Infected/Unique/Contacts", 'i')

                # ======================================================================== process happiness and economy
                # delta_eco_status = CharacterEngine.update_economy(people, args)
                # CharacterEngine.update_happiness(people, delta_eco_status, day_t_instances[:, 2, :].astype(int), args)

            # ===========================================================================disease progression within host
            CovEngine.process_disease_state(people, t, cemetery)

            # ============================================================================================== vaccination

            for vaccinate_event in vaccinate_events:
                if vaccinate_event[0] == day:
                    CovEngine.vaccinate_people(vaccinate_event[1], vaccinate_event[2], people)

            if iteration > 0:
                Logger.update_covid_log(people, new_infected)
                Logger.save_log_files(t, people, locations, log_fine_details)

            # loading route initializing probability matrices based on type of day in the week and containment strategy
            RoutePlanningEngine.set_parameters((t // Time.DAY) % 7)
            bad = 0
            for p in tqdm(people, desc=f'Resetting day {day}'):
                if not p.reset_day(t):
                    bad += 1
            if bad > 0:
                print(f"RESET FAILED {bad}/{len(people)}")

            # =============================================================================== check transporter coverage
            # covered_locations = {loc: False for loc in root.get_locations_according_function(lambda x: True)}
            # for p in people:
            #     if isinstance(p, BusDriver):
            #         for trans_visit in p.route_rep:
            #             covered_locations[trans_visit] = True
            # covered_location_classes = {}
            # for loc in covered_locations.keys():
            #     loc_class = loc.class_name
            #     if loc_class not in covered_location_classes.keys():
            #         covered_location_classes[loc_class] = [0, 0]
            #     covered_location_classes[loc_class][0] += 1
            #     if covered_locations[loc]:
            #         covered_location_classes[loc_class][1] += 1
            # Logger.log(f"Coverage from bus {sum(covered_locations.values())}/{len(covered_locations)}", 'c')
            # Logger.log('\n'.join(
            #     [f"{key}:\t\t\t{covered_location_classes[key][1]} / {covered_location_classes[key][0]}" for key in
            #      covered_location_classes.keys()]), 'c')

            # ======================================================================================= reset test centers
            for tc in test_centers:
                tc.on_reset_day()

            # ==================================== check for gather events on this day and update the routes accordingly
            for event in gather_events:
                if event.day == t // Time.DAY:
                    Logger.log(f'Holding event {event} on this day', 'c')
                    for selected_person in event.select_people(people):
                        new_route = RoutePlanningEngine.add_target_to_route(
                            selected_person.route, Target(event.loc, t + event.time + event.duration, None),
                            t + event.time, t + event.time + event.duration)
                        selected_person.set_route(new_route, t, move2first=True)
            now_time = time.time()
            if day > 0:
                Logger.log(f"Elapsed time {(now_time-elapsed_time)/60:.2f}mins.", 'c')
                Logger.log(f"Per day {(now_time-elapsed_time)/60/(day-start_day+1):.2f}mins.", 'c')
                Logger.log(f"Remaining time {(start_day+days-day+1)*(now_time-elapsed_time)/60/(day-start_day+1):.2f} mins", 'c')
            # clear data
            day_t_instances = []

        # ============================================================================================= process movement

        n_overtime = MovementEngine.process_people_switching(Person.all_people, t)
        MovementEngine.move_people(Person.all_people)
        day_t_instances.append(get_instance(Person.all_people))

        # ============================================================================================== process testing
        if t % testing_freq == 0:
            TestingEngine.testing_procedure(people, test_centers, t)

        # ======================================================================================= spawn new test centers
        # if t % test_center_spawn_check_freq == 0:
        #     test_center = TestCenter.spawn_test_center(test_center_spawn_method, people, test_centers, root.radius,
        #                                                root.radius, args.test_center_r, test_center_spawn_threshold)
        #     if test_center is not None:
        #         print(f"Added new TEST CENTER at {test_center.x} {test_center.y}")
        #         test_centers.append(test_center)

        # ========================================================== check locations for any changes to quarantine state
        ContainmentEngine.check_location_state_updates(root, t)

        update_point_parameters(args)

        # ======================================================================= change routes randomly for some people
        # RoutePlanningEngine.update_routes(root, t)

        # ================================================ overriding daily routes if necessary. (tested positives, etc)
        # for p in people:
        #     if ContainmentEngine.update_route_according_to_containment(p, root, args.containment_strategy, t):
        #         break

        # ============================================================================================== integrity check
        if integrity_test:
            for p in people:
                if p.is_dead():
                    assert isinstance(p.current_loc, Cemetery)  # Dead not in cemetery
                if p.latched_to is None:
                    next_loc = MovementEngine.find_next_location(p)
                    if p.current_loc.depth >= next_loc.depth:  # parent transporting
                        trans_loc = p.current_loc.parent_location
                    else:  # current transporting
                        trans_loc = p.current_loc
                    if trans_loc.override_transport is not None and not isinstance(p, Transporter):
                        if trans_loc.override_transport.override_level <= p.main_trans.override_level:
                            assert p.current_trans == trans_loc.override_transport

        # ====================================================================================== record in daily report
        Logger.update_resource_usage_log()

        Logger.update_person_log(people)

        Time.increment_time_unit()
