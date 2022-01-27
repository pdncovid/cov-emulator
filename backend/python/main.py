import argparse
import os
import time

import numpy as np
from tqdm import tqdm

from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.CovEngine import CovEngine
from backend.python.Logger import Logger
from backend.python.MovementEngine import MovementEngine
from backend.python.PersonFeatureEngine import PersonFeatureEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.TestingEngine import TestingEngine
from backend.python.Time import Time
from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.data.save_classes import all_subclasses, save_array
from backend.python.enums import TestSpawn, ClassNameMaps, Containment, PersonFeatures
from backend.python.functions import count_graph_n, separate_into_classes
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Location import Location
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.Home import Home
from backend.python.location.Stations.BusStation import BusStation
from backend.python.location.TestCenter import TestCenter
from backend.python.point.BusDriver import BusDriver
from backend.python.point.Person import Person
from backend.python.point.Transporter import Transporter
from backend.python.transport.Movement import Movement

# ====================================== PARAMETERS =====================================================
testing_freq = 10
test_center_spawn_check_freq = 10
test_center_spawn_method = TestSpawn.HEATMAP.value
test_center_spawn_threshold = 100


def get_args(name):
    parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
    parser.add_argument('--name', help="Name of the simulation", default=name)
    parser.add_argument('-n', help='target population', default=100)
    parser.add_argument('-i', help='initial infected %', type=int, default=0.01)
    parser.add_argument('-days', help='Number of simulation days', type=int, default=60)

    parser.add_argument('--infect_r', help='infection radius', type=float, default=1)
    parser.add_argument('--common_p', help='common fever probability', type=float, default=0.1)

    parser.add_argument('--containment', help='containment strategy used ', type=int, default=Containment.NONE.value)
    parser.add_argument('--testing', help='testing strategy used (0-Random, 1-Temperature based)', type=int, default=1)
    parser.add_argument('--test_centers', help='Number of test centers', type=int, default=3)
    parser.add_argument('--test_acc', help='Test accuracy', type=float, default=0.80)
    parser.add_argument('--test_center_r', help='Mean radius of coverage from the test center', type=int, default=20)
    parser.add_argument('--asymptotic_t',
                        help='Mean asymptotic period. (Test acc gradually increases with disease age)',
                        type=int, default=14)

    parser.add_argument('--initialize',
                        help='How to initialize the positions (0-Random, 1-From file 2-From probability map)',
                        type=int, default=0)

    return parser.parse_args()


def set_parameters(args):
    Logger('logs', time.strftime(args.name + '%Y.%m.%d-%H.%M.%S', time.localtime()) + '.log', print=True, write=False)

    TestCenter.set_parameters(args.asymptotic_t, args.test_acc)

    # initialize simulator timer
    Time.init()

    # initialize route planner
    RoutePlanningEngine.set_parameters((Time.get_time() // Time.DAY) % 7, args.containment)


# ==================================== END PARAMETERS ====================================================


def update_point_parameters(args):
    for p in Person.all_people:
        p.update_temp(args.common_p)


def get_instance(people):
    x = Person.features[:, PersonFeatures.px.value]
    y = Person.features[:, PersonFeatures.py.value]
    ploc_ids = [p.get_current_location().ID for p in people]
    return x, y, ploc_ids


def executeSim(people, root, gather_events, vaccinate_events, args):
    integrity_test = False
    record_fine_covid = True
    record_fine_person = True
    process_disease_freq = 1  # Time.get_duration(2)
    process_disease_at = process_disease_freq
    days = args.days
    iterations = int(days * 1440 / Time._scale)

    test_name = time.strftime(args.name + '%Y.%m.%d-%H.%M.%S', time.localtime())
    os.makedirs('../../app/src/data/' + test_name)

    # initialize graphs and people
    locations = root.get_locations_according_function(lambda x: True)

    # check house density
    loc_classes = separate_into_classes(root)
    for loc_class in loc_classes.keys():
        if str(Home.__name__) in loc_class.__name__:
            print(loc_class, len(loc_classes[loc_class]))
            pph = len(people) / len(loc_classes[loc_class])
            if pph > 4.5:
                Logger.log(
                    f'Houses are too dense with people. Increase houses or reduce population. People per house is {pph}',
                    'c')
                exit(-1)

    # save initial parameters
    loc_classes = all_subclasses(Location)
    people_classes = all_subclasses(Person)
    movement_classes = all_subclasses(Movement)
    for p in people:
        people_classes.add(p.class_name)
    for l in locations:
        loc_classes.add(l.class_name)
    lc_map = {x: i for i, x in enumerate(loc_classes)}
    pc_map = {x: i for i, x in enumerate(people_classes)}
    mc_map = {x: i for i, x in enumerate(movement_classes)}
    lc_map[None], pc_map[None], mc_map[None], = -1, -1, -1
    ClassNameMaps.lc_map = lc_map
    ClassNameMaps.pc_map = pc_map
    ClassNameMaps.mc_map = mc_map
    save_array('../../app/src/data/' + test_name + '/locs.txt', loc_classes)
    save_array('../../app/src/data/' + test_name + '/people.txt', people_classes)
    save_array('../../app/src/data/' + test_name + '/movement.txt', movement_classes)
    save_array("../../app/src/data/locs.txt", loc_classes)
    save_array("../../app/src/data/people.txt", people_classes)

    # add test centers to medical zones
    test_centers = []
    classes = separate_into_classes(root)
    if MedicalZone in classes.keys():
        for mz in classes[MedicalZone]:
            test_center = TestCenter(mz.px, mz.py, mz.radius)
            test_centers.append(test_center)

    # find cemeteries
    cemetery = classes[Cemetery]

    # initial iterations to initialize positions of the people
    for t in range(5):
        print(f"initializing {t}")
        MovementEngine.move_people(Person.all_people)

    Logger.log(f"{len(people)} {count_graph_n(root)}", 'i')
    Logger.log(f"{len(people)} {count_graph_n(root)}", 'c')
    Logger.log_graph(root)

    contacts, n_con, new_infected = {_i: [] for _i in range(len(people))}, np.zeros(len(people)), []

    day_t_instances = []
    # main iteration loop
    for i in range(iterations):
        t = Time.get_time()

        print(f"\r=========================Iteration: {t} {Time.i_to_time(t)}======================", end='')

        # reset day
        if t % Time.DAY == 0:
            day_t_instances = np.array(day_t_instances)
            # disease progression within host
            CovEngine.process_recovery(people, t)
            CovEngine.process_death(people, t, cemetery)

            # vaccination
            day = t // Time.DAY
            for vaccinate_event in vaccinate_events:
                if vaccinate_event[0] == day:
                    CovEngine.vaccinate_people(vaccinate_event[1], vaccinate_event[2], people)

            if t > 0:
                Logger.save_log_files(test_name, t, people, locations)
                # process happiness index
                Person.features[:, PersonFeatures.happiness.value] = PersonFeatureEngine.process_happiness(
                    day_t_instances[:, 0, :], day_t_instances[:, 1, :], day_t_instances[:, 2, :].astype(int),
                    Person.features[:, PersonFeatures.happiness.value], containment=args.containment)
            # loading route initializing probability matrices based on type of day in the week and containment strategy
            RoutePlanningEngine.set_parameters((t // Time.DAY) % 7, args.containment)
            bad = 0
            for p in tqdm(people, desc='Resetting day'):
                if not p.reset_day(t):
                    bad += 1
            if bad > 0:
                print(f"RESET FAILED {bad}/{len(people)}")

            # check transporter coverage
            # covered_locations = {loc: False for loc in root.get_locations_according_function(lambda x: True)}
            # for p in people:
            #     if isinstance(p, BusDriver):
            #         for trans_visit in p.route_rep:
            #             covered_locations[trans_visit] = True
            # covered_location_classes = {}
            # for loc in covered_locations.keys():
            #     loc_class = loc.__class__.__name__
            #     if loc_class not in covered_location_classes.keys():
            #         covered_location_classes[loc_class] = [0, 0]
            #     covered_location_classes[loc_class][0] += 1
            #     if covered_locations[loc]:
            #         covered_location_classes[loc_class][1] += 1
            # Logger.log(f"Coverage from bus {sum(covered_locations.values())}/{len(covered_locations)}", 'c')
            # Logger.log('\n'.join(
            #     [f"{key}:\t\t\t{covered_location_classes[key][1]} / {covered_location_classes[key][0]}" for key in
            #      covered_location_classes.keys()]), 'c')

            # reset test centers
            for tc in test_centers:
                tc.on_reset_day()

            # check for gather events on this day and update the routes accordingly.
            for event in gather_events:
                if event.day == t // Time.DAY:
                    Logger.log(f'Holding event {event} on this day', 'i')
                    for selected_person in event.select_people(people):
                        new_route = RoutePlanningEngine.add_target_to_route(
                            selected_person.route, Target(event.loc, t + event.time + event.duration, None),
                            t + event.time, t + event.time + event.duration)
                        selected_person.set_route(new_route, t, move2first=True)

            # clear data
            day_t_instances = []

        # process movement
        MovementEngine.process_people_switching(root, t)
        MovementEngine.move_people(Person.all_people)
        day_t_instances.append(get_instance(Person.all_people))

        # process transmission and recovery
        if t > process_disease_at:
            n_con, contacts, new_infected = TransmissionEngine.disease_transmission(people, t, args.infect_r)
            process_disease_at += process_disease_freq

            Logger.log(f"{len(new_infected)}/{sum(n_con > 0)}/{int(sum(n_con))} Infected/Unique/Contacts", 'i')

        # process testing
        if t % testing_freq == 0:
            TestingEngine.testing_procedure(people, test_centers, t)

        # spawn new test centers
        # if t % test_center_spawn_check_freq == 0:
        #     test_center = TestCenter.spawn_test_center(test_center_spawn_method, people, test_centers, root.radius,
        #                                                root.radius, args.test_center_r, test_center_spawn_threshold)
        #     if test_center is not None:
        #         print(f"Added new TEST CENTER at {test_center.x} {test_center.y}")
        #         test_centers.append(test_center)

        # check locations for any changes to quarantine state
        ContainmentEngine.check_location_state_updates(root, t)

        update_point_parameters(args)

        # change routes randomly for some people
        # RoutePlanningEngine.update_routes(root, t)

        # overriding daily routes if necessary. (tested positives, etc)
        # for p in people:
        #     if ContainmentEngine.update_route_according_to_containment(p, root, args.containment, t):
        #         break

        # =================================== integrity check ======================================================
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
        if record_fine_covid:
            Logger.update_covid_log(people)
        if record_fine_person:
            Logger.update_person_log(people, n_con, contacts)

        Time.increment_time_unit()
