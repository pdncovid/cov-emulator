import sys
import numpy as np
import argparse
from backend.python.enums import Mobility, Shape, TestSpawn, Containment
from backend.python.functions import   get_random_element, \
    separate_into_classes
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Residential.Home import Home
from backend.python.main import main, work_map
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Bus import Bus
from backend.python.transport.CommercialZoneBus import CommercialZoneBus
from backend.python.transport.Tuktuk import Tuktuk
from backend.python.transport.Walk import Walk

"""
TODO: 
Infection using contagious areas
"""
iterations = 100000
testing_freq = 10
test_center_spawn_check_freq = 10
test_center_spawn_method = TestSpawn.HEATMAP.value
test_center_spawn_threshold = 100

parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
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


def initialize_graph():
    root = UrbanBlock(Shape.CIRCLE.value, 0, 0, "D1", r=100)
    root.add_sub_location(Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3))
    return root


def initialize2():
    # initialize people

    people = [TuktukDriver() for _ in range(10)]
    people += [CommercialWorker() for _ in range(100)]
    for _ in range(2):
        idx = np.random.randint(0,len(people))
        people[idx].set_infected(0, people[idx], args.common_p)

    # initialize location tree
    root = UrbanBlock(Shape.CIRCLE.value, 0, 0, "D1", r=100)
    root.add_sub_location(Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3))
    loc_classes = separate_into_classes(root)

    # set random routes for each person and set their main transportation method
    walk = Walk(Mobility.RANDOM.value)
    bus = Bus(Mobility.RANDOM.value)
    combus = CommercialZoneBus(Mobility.RANDOM.value)
    tuktuk = Tuktuk(Mobility.RANDOM.value)
    main_trans = [tuktuk]

    for person in people:
        person.set_home_loc(get_random_element(loc_classes[Home]))
        person.work_loc = person.find_closest(work_map[person.__class__], person.home_loc)  # todo
        target_classes_or_objs = [person.home_loc, person.work_loc]
        person.set_random_route(root, 0, target_classes_or_objs=target_classes_or_objs)
        if person.main_trans is None:
            person.main_trans = get_random_element(main_trans)

    return people, root


if __name__ == "__main__":
    sys.setrecursionlimit(1000000)
    main(initializer=initialize2)
