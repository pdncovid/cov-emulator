import sys
import time
import warnings

import numpy as np
import argparse
import matplotlib.pyplot as plt
import pandas as pd

from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Logger import Logger
from backend.python.CovEngine import CovEngine
from backend.python.MovementEngine import MovementEngine
from backend.python.RoutePlanningEngine import RoutePlanningEngine
from backend.python.TestingEngine import TestingEngine
from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.Visualizer import Visualizer
from backend.python.const import DAY
from backend.python.enums import Mobility, Shape, TestSpawn, Containment
from backend.python.functions import bs, count_graph_n, get_random_element, \
    separate_into_classes
from backend.python.Time import Time
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Commercial.CommercialBuilding import CommercialBuilding
from backend.python.location.Commercial.CommercialZone import CommercialZone
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.Home import Home
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.location.TestCenter import TestCenter
from backend.python.point.CommercialZoneBusDriver import CommercialZoneBusDriver
from backend.python.point.Person import Person
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Bus import Bus
from backend.python.transport.CommercialZoneBus import CommercialZoneBus
from backend.python.transport.Movement import Movement
from backend.python.transport.Walk import Walk

"""
TODO: 
Infection using contagious areas
"""
iterations = 10000
testing_freq = 10
test_center_spawn_check_freq = 10
test_center_spawn_method = TestSpawn.HEATMAP.value
test_center_spawn_threshold = 100

parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
parser.add_argument('-n', help='target population', default=10)
parser.add_argument('-i', help='initial infected', type=int, default=2)
parser.add_argument('-H', help='height', type=int, default=102)
parser.add_argument('-W', help='width', type=int, default=102)

parser.add_argument('--infect_r', help='infection radius', type=float, default=1)
parser.add_argument('--common_p', help='common fever probability', type=float, default=0.1)

parser.add_argument('--containment', help='containment strategy used ', type=int,
                    default=Containment.QUARANTINECENTER.value)
parser.add_argument('--testing', help='testing strategy used (0-Random, 1-Temperature based)', type=int, default=1)
parser.add_argument('--test_centers', help='Number of test centers', type=int, default=3)
parser.add_argument('--test_acc', help='Test accuracy', type=float, default=0.80)
parser.add_argument('--test_center_r', help='Mean radius of coverage from the test center', type=int, default=20)
parser.add_argument('--asymptotic_t', help='Mean asymptotic period. (Test acc gradually increases with disease age)',
                    type=int, default=14)

parser.add_argument('--initialize',
                    help='How to initialize the positions (0-Random, 1-From file 2-From probability map)',
                    type=int, default=0)

args = parser.parse_args()

work_map = {CommercialWorker: CommercialZone,
            BusDriver: None,
            TuktukDriver: None,
            CommercialZoneBusDriver: CommercialBuilding}


def initialize_graph():
    root = UrbanBlock(Shape.CIRCLE.value, 0, 0, "D1", r=100)
    root.add_sub_location(Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3))
    return root


def initialize():
    # initialize people

    people = [CommercialWorker() for _ in range(args.n)]
    people += [BusDriver() for _ in range(5)]
    people += [TuktukDriver() for _ in range(10)]
    # people += [CommercialZoneBusDriver() for _ in range(5)]

    for _ in range(args.i):
        idx = np.random.randint(0, args.n)
        people[idx].set_infected(0, people[idx], args.common_p)

    # initialize location tree
    root = UrbanBlock(Shape.CIRCLE.value, 0, 0, "D1", r=100)
    root.add_sub_location(Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3))
    loc_classes = separate_into_classes(root)

    # set random routes for each person and set their main transportation method
    walk = Walk(np.random.randint(1, 10), Mobility.RANDOM.value)
    bus = Bus(np.random.randint(60, 80), Mobility.RANDOM.value)
    combus = CommercialZoneBus(np.random.randint(60, 80), Mobility.RANDOM.value)
    main_trans = [bus]

    for person in people:

        person.set_home_loc(get_random_element(loc_classes[Home]))  # todo
        person.work_loc = person.find_closest(work_map[person.__class__], person.home_loc)  # todo

        target_classes_or_objs = [person.home_loc, person.work_loc]
        person.set_random_route(root, 0, target_classes_or_objs=target_classes_or_objs)
        if person.main_trans is None:
            person.main_trans = get_random_element(main_trans)

    return people, root


def update_point_parameters():
    for p in Person.all_people:
        p.update_temp(args.common_p)


def main(initializer):
    PLOT = True
    global log
    log = Logger('logs', time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime()) + '.log', print=True, write=False)

    TestCenter.set_parameters(args.asymptotic_t, args.test_acc)

    # initialize graphs and people
    people, root = initializer()
    log.log(f"{len(people)} {count_graph_n(root)}", 'i')
    log.log(f"{len(people)} {count_graph_n(root)}", 'c')
    log.log_graph(root)

    # DAILY REPORT
    df = pd.DataFrame(columns=['loc', 'person', 'time', 'loc_class'])
    df = df.astype(dtype={"loc": "int64", "person": "int64", "time": "int64", "loc_class": 'object'})
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
    if PLOT:
        Visualizer.initialize(root, test_centers, people, args.H, args.W)

    # initial iterations to initialize positions of the people
    for t in range(5):
        print(f"initializing {t}")
        MovementEngine.move_people(Person.all_people)

    # main iteration loop
    for i in range(iterations):
        t = Time.get_time()
        log.log(f"Iteration: {t} {Time.i_to_time(t)}", 'c')
        log.log(f"=========================Iteration: {t} {Time.i_to_time(t)}======================", 'd')
        log.log_people(people)

        # process movement
        MovementEngine.process_people_switching(root, t)
        MovementEngine.move_people(Person.all_people)

        # process transmission and recovery
        TransmissionEngine.disease_transmission(people, t, args.infect_r)
        CovEngine.process_recovery(people, t)
        CovEngine.process_death(people, t, cemetery)

        # process testing
        if t % testing_freq == 0:
            TestingEngine.testing_procedure(people, test_centers, t)

        # spawn new test centers
        if t % test_center_spawn_check_freq == 0:
            test_center = TestCenter.spawn_test_center(test_center_spawn_method, people, test_centers, args.H,
                                                       args.W, args.test_center_r, test_center_spawn_threshold)
            if test_center is not None:
                print(f"Added new TEST CENTER at {test_center.x} {test_center.y}")
                test_centers.append(test_center)

        # check locations for any changes to quarantine state
        ContainmentEngine.check_location_state_updates(root, t)

        update_point_parameters()

        # change routes randomly for some people
        # RoutePlanningEngine.update_routes(root, t)

        # overriding daily routes if necessary. (tested positives, etc)
        for p in people:
            if ContainmentEngine.update_route_according_to_containment(p, root, args.containment, t):
                break

        # reset day

        if t % DAY == 0:
            good = True
            for p in people:
                if not p.reset_day(t):
                    good = False
            if not good:
                raise Exception("Day reset failed")

        # record in daily report
        tmp_list = []
        # _str_i = len("<class backend.python.location")
        for p in people:
            cur = p.get_current_location()
            person = p.ID
            tmp_list.append({'loc': cur.ID, 'person': person, 'time': t, 'loc_class': cur.__class__.__name__})
        df = df.append(pd.DataFrame(tmp_list))
        # ==================================== plotting ==============================================================
        if PLOT:
            if t % (DAY // 10) == 0:
                plt.pause(0.001)
                Visualizer.plot_map_and_points(root, people, test_centers, args.H, args.W, t)
                # update_figure(fig, ax, sc, hm, root, people, test_centers, args.H, args.W, t)

                Visualizer.plot_position_timeline(df, root)
                Visualizer.plot_info(people)

        Time.increment_time_unit()


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    main(initializer=initialize)
