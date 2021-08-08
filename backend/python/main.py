import os
import sys
import time

import numpy as np
import argparse
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Logger import Logger
from backend.python.CovEngine import CovEngine
from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.TestingEngine import TestingEngine
from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.Visualizer import Visualizer
from backend.python.const import work_map
from backend.python.data.save_classes import all_subclasses, save_array
from backend.python.enums import Mobility, Shape, TestSpawn, Containment
from backend.python.functions import count_graph_n, get_random_element, separate_into_classes
from backend.python.Time import Time
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.Location import Location
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
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Bus import Bus
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

    people += [BusDriver() for _ in range(int(0.05 * args.n))]
    people += [TuktukDriver() for _ in range(int(0.05 * args.n))]
    people += [CommercialZoneBusDriver() for _ in range(int(0.03 * args.n))]
    people += [SchoolBusDriver() for _ in range(int(0.02 * args.n))]

    for _ in range(args.i):
        idx = np.random.randint(0, args.n)
        people[idx].set_infected(0, people[idx], args.common_p)

    # initialize location tree
    root = DenseDistrict(Shape.CIRCLE.value, 0, 0, "D1", r=500)
    root.add_sub_location(Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3))
    loc_classes = separate_into_classes(root)

    # set random routes for each person and set their main transportation method
    walk = Walk(Mobility.RANDOM.value)
    bus = Bus(Mobility.RANDOM.value)
    combus = CommercialZoneBus(Mobility.RANDOM.value)
    schoolbus = SchoolBus(Mobility.RANDOM.value)
    tuktuk = Tuktuk(Mobility.RANDOM.value)
    main_trans = [bus, tuktuk, walk]

    for person in people:

        person.set_home_loc(get_random_element(loc_classes[Home]))  # todo
        person.home_weekend_loc = person.find_closest('Home', person.home_loc.parent_location, find_from_level=2)
        person.work_loc = person.find_closest(work_map[person.__class__], person.home_loc, find_from_level=-1)  # todo

        if person.main_trans is None:
            person.main_trans = get_random_element(main_trans)

    return people, root


def update_point_parameters(args):
    for p in Person.all_people:
        p.update_temp(args.common_p)


def main(initializer, args):
    test_name = time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime())
    os.makedirs('data/' + test_name)

    loc_classes = all_subclasses(Location)
    people_classes = all_subclasses(Person)
    movement_classes = all_subclasses(Movement)
    loc_classes_map = {x: i for i, x in enumerate(loc_classes)}
    people_classes_map = {x: i for i, x in enumerate(people_classes)}
    movement_classes_map = {x: i for i, x in enumerate(movement_classes)}
    save_array('data/' + test_name + '/locs.txt', loc_classes)
    save_array('data/' + test_name + '/people.txt', people_classes)
    save_array('data/' + test_name + '/movement.txt', movement_classes_map)
    save_array("../../app/src/data/locs.txt", loc_classes)
    save_array("../../app/src/data/people.txt", people_classes)

    plot = True
    global log
    log = Logger('logs', time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime()) + '.log', print=True, write=False)
    set_parameters(args)

    # initialize simulator timer
    Time.init()

    # initialize graphs and people
    people, root = initializer()
    log.log(f"{len(people)} {count_graph_n(root)}", 'i')
    log.log(f"{len(people)} {count_graph_n(root)}", 'c')
    log.log_graph(root)

    # DAILY REPORT
    df = pd.DataFrame(columns=[])
    # df = df.astype(dtype={"loc": "int64", "person": "int64", "time": "int64", "loc_class": 'object'})
    # df.set_index('time')

    # add test centers to medical zones
    test_centers = []
    classes = separate_into_classes(root)
    for mz in classes[MedicalZone]:
        test_center = TestCenter(mz.x, mz.y, mz.radius)
        test_centers.append(test_center)

    # find cemeteries
    cemetery = classes[Cemetery]

    # initialize plots
    if plot:
        Visualizer.initialize(root, test_centers, people, loc_classes_map, root.radius, root.radius)

    # initial iterations to initialize positions of the people
    for t in range(5):
        print(f"initializing {t}")
        MovementEngine.move_people(Person.all_people)
    process_disease_freq = Time.get_duration(2)
    process_disease_at = process_disease_freq

    # main iteration loop
    for i in range(iterations):
        t = Time.get_time()

        log.log(f"Iteration: {t} {Time.i_to_time(t)}", 'c')
        log.log(f"=========================Iteration: {t} {Time.i_to_time(t)}======================", 'd')
        log.log_people(people)

        # reset day
        if t % Time.DAY == 0:
            good = True

            for p in tqdm(people, desc='Resetting day'):
                if not p.reset_day(t):
                    good = False
            if not good:
                a = input("RESET FAILED")
            #     raise Exception("Day reset failed")

        # process movement
        MovementEngine.process_people_switching(root, t)
        MovementEngine.move_people(Person.all_people)

        # process transmission and recovery
        if t > process_disease_at:
            TransmissionEngine.disease_transmission(people, t, args.infect_r)
            CovEngine.process_recovery(people, t)
            CovEngine.process_death(people, t, cemetery)
            process_disease_at += process_disease_freq

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

        # ==================================== plotting ==============================================================
        if plot:
            # record in daily report
            tmp_list = []
            mins = Time.i_to_minutes(t)
            for p in people:
                cur = p.get_current_location()
                tmp_list.append(
                    {

                        'person': p.ID,
                        'location': cur.ID,
                        'x': round(Person.all_positions[p.ID][0]*100)/100,
                        'y': round(Person.all_positions[p.ID][1]*100)/100,
                        'person_class': people_classes_map[p.__class__.__name__],
                        'loc_class': loc_classes_map[cur.__class__.__name__],
                        'cur_movement': movement_classes_map[p.current_trans.__class__.__name__],
                        'cur_tar_idx': len(p.route) - 1 if p.is_day_finished else p.current_target_idx,
                        'route_len': len(p.route),

                        'time': mins,
                    }
                )
            df = df.append(pd.DataFrame(tmp_list))
            if t % (Time.DAY // 1) == 0:
                pd.DataFrame.to_csv(df, f"data/{test_name}/{t:05d}.csv")
                plt.pause(0.001)
                Visualizer.plot_map_and_points(root, people, test_centers, root.radius, root.radius, t)
                Visualizer.plot_position_timeline(df, root)
                Visualizer.plot_info(people)

        Time.increment_time_unit()


if __name__ == "__main__":
    global args
    parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
    parser.add_argument('-n', help='target population', default=100)
    parser.add_argument('-i', help='initial infected', type=int, default=2)

    parser.add_argument('--infect_r', help='infection radius', type=float, default=1)
    parser.add_argument('--common_p', help='common fever probability', type=float, default=0.1)

    parser.add_argument('--containment', help='containment strategy used ', type=int,
                        default=Containment.QUARANTINECENTER.value)
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
