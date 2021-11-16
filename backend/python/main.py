import os
import sys
import time

import numpy as np
import argparse
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.GatherEvent import GatherEvent
from backend.python.Logger import Logger
from backend.python.CovEngine import CovEngine
from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.Target import Target
from backend.python.TestingEngine import TestingEngine
from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.Visualizer import Visualizer
from backend.python.const import work_map
from backend.python.data.save_classes import all_subclasses, save_array
from backend.python.enums import Mobility, Shape, TestSpawn, Containment, State, ClassNameMaps
from backend.python.functions import count_graph_n, get_random_element, separate_into_classes
from backend.python.Time import Time
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.GatheringPlace import GatheringPlace
from backend.python.location.Location import Location
from backend.python.location.Medical.COVIDQuarantineZone import COVIDQuarantineZone
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.Home import Home
from backend.python.point.BusDriver import BusDriver
from backend.python.location.TestCenter import TestCenter
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.CommercialZoneBusDriver import CommercialZoneBusDriver
from backend.python.point.GarmentAdmin import GarmentAdmin
from backend.python.point.GarmentWorker import GarmentWorker
from backend.python.point.Person import Person
from backend.python.point.SchoolBusDriver import SchoolBusDriver
from backend.python.point.Student import Student
from backend.python.point.Transporter import Transporter
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Bus import Bus
from backend.python.transport.Car import Car
from backend.python.transport.CommercialZoneBus import CommercialZoneBus
from backend.python.transport.Movement import Movement
from backend.python.transport.SchoolBus import SchoolBus
from backend.python.transport.Tuktuk import Tuktuk
from backend.python.transport.Walk import Walk

# ====================================== PARAMETERS =====================================================

iterations = 10000
testing_freq = 10
test_center_spawn_check_freq = 10
test_center_spawn_method = TestSpawn.HEATMAP.value
test_center_spawn_threshold = 100


def set_parameters(args):
    TestCenter.set_parameters(args.asymptotic_t, args.test_acc)


# ==================================== END PARAMETERS ====================================================

def initialize():
    # initialize people
    people = []
    people += [CommercialWorker() for _ in range(int(0.3 * args.n))]
    people += [GarmentWorker() for _ in range(int(0.3 * args.n))]
    people += [GarmentAdmin() for _ in range(int(0.03 * args.n))]
    people += [Student() for _ in range(int(0.3 * args.n))]

    people += [BusDriver() for _ in range(int(0.15 * args.n))]
    people += [TuktukDriver() for _ in range(int(0.05 * args.n))]
    # people += [CommercialZoneBusDriver() for _ in range(int(0.03 * args.n))]
    # people += [SchoolBusDriver() for _ in range(int(0.02 * args.n))]

    for _ in range(args.i):
        idx = np.random.randint(0, len(people))
        people[idx].set_infected(0, people[idx], args.common_p)

    # initialize location tree
    root = DenseDistrict(Shape.CIRCLE.value, 0, 0, "D1", r=500)
    root.add_sub_location(Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3))
    loc_classes = separate_into_classes(root)

    # set random routes for each person and set their main transportation method
    # walk = Walk(Mobility.RANDOM.value) # DO NOT Add walk as a main transport!!! At minimum a person uses the bus
    # combus = CommercialZoneBus(Mobility.RANDOM.value)
    # schoolbus = SchoolBus(Mobility.RANDOM.value)

    bus = Bus()
    car = Car()
    tuktuk = Tuktuk()
    main_trans = [bus]

    for person in people:
        if person.main_trans is None:
            person.main_trans = get_random_element(main_trans)
        person.set_home_loc(get_random_element(loc_classes[Home]))  # todo
        person.home_weekend_loc = person.find_closest('Home', person.home_loc.parent_location, find_from_level=2)
        if work_map[person.__class__] is None:
            person.work_loc = person.home_loc
        else:
            person.work_loc = person.find_closest(work_map[person.__class__], person.home_loc,
                                                  find_from_level=-1)  # todo

    return people, root


def update_point_parameters(args):
    for p in Person.all_people:
        p.update_temp(args.common_p)


def main(initializer, args):
    integrity_test = False
    record_fine_covid = True
    record_fine_person = True
    plot = False
    n_events = 10
    process_disease_freq = 1  # Time.get_duration(2)
    process_disease_at = process_disease_freq

    test_name = time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime())
    os.makedirs('../../app/src/data/' + test_name)

    global log
    log = Logger('logs', time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime()) + '.log', print=True, write=False)
    set_parameters(args)

    # initialize simulator timer
    Time.init()

    # initialize graphs and people
    people, root = initializer()
    locations = root.get_locations_according_function(lambda x: True)

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

    # initialize gathering events
    gather_places = root.get_locations_according_function(lambda l: isinstance(l, GatheringPlace))
    gather_criteria = [lambda x: isinstance(x, Student),
                       lambda x: isinstance(x, CommercialWorker),
                       lambda x: 14 < x.age < 45]
    gather_events = []
    for ge in range(n_events):
        gathering_place = get_random_element(gather_places)
        if gathering_place is None:
            continue
        day = np.random.randint(0, 7)
        start_time = Time.get_random_time_between(0, 16, 0, 18, 0)
        duration = Time.get_duration(2)
        gather_events.append(GatherEvent(day, start_time, duration, gathering_place,
                                         np.random.randint(int(args.n * 0.10)),
                                         get_random_element(gather_criteria)))

    # add test centers to medical zones
    test_centers = []
    classes = separate_into_classes(root)
    if MedicalZone in classes.keys():
        for mz in classes[MedicalZone]:
            test_center = TestCenter(mz.x, mz.y, mz.radius)
            test_centers.append(test_center)

    # find cemeteries
    cemetery = classes[Cemetery]

    # # initialize plots
    if plot:
        Visualizer.initialize(root, test_centers, people, lc_map, root.radius, root.radius)

    # initial iterations to initialize positions of the people
    for t in range(5):
        print(f"initializing {t}")
        MovementEngine.move_people(Person.all_people)

    # DAILY REPORT
    df_detailed_person = pd.DataFrame(columns=[])
    df_detailed_covid = pd.DataFrame(columns=[])

    log.log(f"{len(people)} {count_graph_n(root)}", 'i')
    log.log(f"{len(people)} {count_graph_n(root)}", 'c')
    log.log_graph(root)

    contacts, n_con, new_infected = {_i:[] for _i in range(len(people))}, np.zeros(len(people)), []
    # main iteration loop
    for i in range(iterations):
        t = Time.get_time()

        # log.log(f"Iteration: {t} {Time.i_to_time(t)}", 'c')
        log.log(f"=========================Iteration: {t} {Time.i_to_time(t)}======================", 'c')
        log.log_people(people)

        # reset day
        if t % Time.DAY == 0:
            if t > 0:
                pd.DataFrame.to_csv(pd.DataFrame([p.get_description_dict() for p in people]),
                                    f"../../app/src/data/{test_name}/{int(t // Time.DAY) - 1:05d}_person_info.csv")
                pd.DataFrame.to_csv(pd.DataFrame([l.get_description_dict() for l in locations]),
                                    f"../../app/src/data/{test_name}/{int(t // Time.DAY) - 1:05d}_location_info.csv")
                pd.DataFrame.to_csv(df_detailed_person,
                                    f"../../app/src/data/{test_name}/{int(t // Time.DAY) - 1:05d}.csv")
                pd.DataFrame.to_csv(df_detailed_covid,
                                    f"../../app/src/data/{test_name}/{int(t // Time.DAY) - 1:05d}_cov_info.csv")
                df_detailed_person = pd.DataFrame(columns=[])
                df_detailed_covid = pd.DataFrame(columns=[])

            # loading route initializing probability matrices based on type of day in the week and containment strategy
            RoutePlanningEngine.set_parameters((t // Time.DAY) % 7, args.containment)
            good = True
            for p in tqdm(people, desc='Resetting day'):
                if not p.reset_day(t):
                    good = False
            if not good:
                a = input("RESET FAILED")

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

        # process movement
        MovementEngine.process_people_switching(root, t)
        MovementEngine.move_people(Person.all_people)

        # process transmission and recovery
        if t > process_disease_at:
            n_con, contacts, new_infected = TransmissionEngine.disease_transmission(people, t, args.infect_r)
            CovEngine.process_recovery(people, t)
            CovEngine.process_death(people, t, cemetery)
            process_disease_at += process_disease_freq

            Logger.log(f"{len(new_infected)}/{sum(n_con > 0)}/{int(sum(n_con))} Infected/Unique/Contacts", 'e')

        # process testing
        if t % testing_freq == 0:
            TestingEngine.testing_procedure(people, test_centers, t)

        # spawn new test centers
        if t % test_center_spawn_check_freq == 0:
            test_center = TestCenter.spawn_test_center(test_center_spawn_method, people, test_centers, root.radius,
                                                       root.radius, args.test_center_r, test_center_spawn_threshold)
            if test_center is not None:
                print(f"Added new TEST CENTER at {test_center.x} {test_center.y}")
                test_centers.append(test_center)

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
        # if integrity_test:
        #     for p in people:
        #         if p.is_dead():
        #             assert isinstance(p.current_loc, Cemetery)  # Dead not in cemetery
        #         if p.latched_to is None:
        #             next_loc = MovementEngine.find_next_location(p)
        #             if p.current_loc.depth >= next_loc.depth:  # parent transporting
        #                 trans_loc = p.current_loc.parent_location
        #             else:  # current transporting
        #                 trans_loc = p.current_loc
        #             if trans_loc.override_transport is not None and not isinstance(p, Transporter):
        #                 if trans_loc.override_transport.override_level <= p.main_trans.override_level:
        #                     assert p.current_trans == trans_loc.override_transport

        # ====================================================================================== record in daily report
        mins = Time.i_to_minutes(t)
        if record_fine_covid:
            covid_stats = {State(i.value).name: 0 for i in State}
            covid_stats['time'] = mins
            covid_stats['CUM_TESTED_POSITIVE'] = 0
            covid_stats['IN_QUARANTINE_CENTER'] = 0
            covid_stats['IN_QUARANTINE'] = 0
            for p in people:
                covid_stats[State(p.state).name] += 1
                covid_stats['CUM_TESTED_POSITIVE'] += 1 if p.is_tested_positive() else 0
                covid_stats['IN_QUARANTINE_CENTER'] += 1 if isinstance(p.get_current_location(),
                                                                       COVIDQuarantineZone) else 0
                covid_stats['IN_QUARANTINE'] += 1 if p.get_current_location().quarantined else 0

            covid_stats["CUM_CASES"] = covid_stats[State.INFECTED.name] + covid_stats[State.DEAD.name] + \
                                       covid_stats[State.RECOVERED.name]
            df_detailed_covid = df_detailed_covid.append(pd.DataFrame([covid_stats]))
        if record_fine_person:
            person_details_list = []
            for p in people:
                cur = p.get_current_location()
                fine_details_p = p.get_fine_description_dict(mins)
                fine_details_p['n_contacts'] = n_con[p.ID]
                fine_details_p['contacts'] = ' '.join(map(str, contacts[p.ID]))  # directed edges from infected to sus
                person_details_list.append(fine_details_p)
            df_detailed_person = df_detailed_person.append(pd.DataFrame(person_details_list))

        Time.increment_time_unit()


if __name__ == "__main__":
    global args
    parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
    parser.add_argument('-n', help='target population', default=1000)
    parser.add_argument('-i', help='initial infected', type=int, default=10)

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

    args = parser.parse_args()

    sys.setrecursionlimit(1000000)
    main(initialize, args)
