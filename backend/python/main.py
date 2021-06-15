import time

import numpy as np
import argparse
import matplotlib.pyplot as plt

from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Logger import Logger
from backend.python.CovEngine import CovEngine
from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.Visualizer import init_figure, update_figure, plot_info
from backend.python.const import DAY
from backend.python.enums import Mobility, Shape, State, TestSpawn, Containment
from backend.python.functions import bs, i_to_time, get_duration, count_graph_n
from backend.python.location.Blocks.UrbanBlock import UrbanBlock
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Commercial.CommercialZone import CommercialZone
from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.Medical.MedicalZone import MedicalZone
from backend.python.location.Residential.ResidentialZone import ResidentialZone
from backend.python.location.Location import Location
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.TestCenter import TestCenter
from backend.python.transport.Bus import Bus
from backend.python.transport.TransportVehicle import TransportVehicle
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
parser.add_argument('-n', help='target population', default=10000)
parser.add_argument('-H', help='height', type=int, default=1002)
parser.add_argument('-W', help='width', type=int, default=1002)
parser.add_argument('-i', help='initial infected', type=int, default=10)

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
    root = DenseDistrict(Shape.CIRCLE.value, 0, 0, "D1", r=1000)
    cemetery = Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3)

    root.add_sub_location(cemetery)
    leaves = []

    def dfs(rr: Location):
        if len(rr.locations) == 0:
            leaves.append(rr)
        for child in rr.locations:
            dfs(child)

    dfs(root)

    for leaf in leaves:
        leaf.override_transport = Walk(0.5, Mobility.RANDOM.value)

    return root, leaves


def initialize():
    n = args.n
    i = args.i

    # initialize people
    if args.initialize == 0:  # Random
        points = [CommercialWorker() for _ in range(n)]
    elif args.initialize == 1:
        raise NotImplemented()
    elif args.initialize == 2:
        raise NotImplemented()
    else:
        raise NotImplemented()

    for _ in range(i):
        idx = np.random.randint(0, n)
        points[idx].set_infected(0, points[idx], args.common_p)

    # initialize location tree
    root, leaves = initialize_graph()

    # set random routes for each person and set their main transportation method
    walk = Walk(np.random.randint(1, 10), Mobility.RANDOM.value)
    bus = Bus(np.random.randint(10, 20), Mobility.RANDOM.value)
    main_trans = [walk, bus]
    for point in points:
        point.set_random_route(root, 0, common_route_classes=get_common_route(point))
        point.main_trans = main_trans[np.random.randint(0, len(main_trans))]

    # setting up bus routes
    def dfs(rr: Location):
        bus.initialize_locations(rr)  # set up bus routes
        if isinstance(rr.override_transport, TransportVehicle):
            rr.override_transport.initialize_locations(rr)
        for child in rr.locations:
            dfs(child)

    dfs(root)

    return points, root


def disease_transmission(points, t):
    x, y = np.array([p.x for p in points]), np.array([p.y for p in points])
    state = np.array([p.state for p in points])

    r = args.infect_r

    contacts, distance, sourceid = TransmissionEngine.get_close_contacts_and_distance(x, y, state, r)

    new_infected = TransmissionEngine.transmit_disease(points, contacts, distance, sourceid, t)

    log.log(f"""{new_infected}/{sum(contacts > 0)}/{int(sum(contacts))}/{sum(
        state == State.INFECTED.value)} Infected/Unique/Contacts/Active""", 'd')


def update_point_parameters(points):
    for i in range(args.n):
        points[i].update_temp(args.common_p)


def testing_procedure(points, test_centers, t):
    x, y = np.array([p.x for p in points]), np.array([p.y for p in points])
    xs_idx = np.argsort(x)
    ys_idx = np.argsort(y)
    xs = x[xs_idx]
    ys = y[ys_idx]

    test_subjects = set()
    tested_on = np.zeros((len(points)), dtype=int)

    for i in range(len(test_centers)):  # iterate through test centers

        r = test_centers[i].r

        x_idx_r = bs(xs, test_centers[i].x + r)
        x_idx_l = bs(xs, test_centers[i].x - r)  # + 1

        y_idx_r = bs(ys, test_centers[i].y + r)
        y_idx_l = bs(ys, test_centers[i].y - r)  # + 1

        close_points = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r])
        for close_point in close_points:
            test_subjects.add(close_point)
            tested_on[close_point] = i
    test_count = np.zeros(len(test_centers), dtype=int)
    for p_idx in test_subjects:
        if test_count[tested_on[p_idx]] >= test_centers[tested_on[p_idx]].max_tests:
            continue
        test_centers[tested_on[p_idx]].test(points[p_idx], t, args)
        test_count[tested_on[p_idx]] += 1


def get_common_route(point):
    if isinstance(point, CommercialWorker):
        return [ResidentialZone, CommercialZone]


def get_alternate_route(point):
    if point.temp > point.infect_temperature[0]:
        return [MedicalZone, CommercialZone]
    return get_common_route(point)[1:]


def main():
    PLOT = True
    global log
    log = Logger('logs', time.strftime('%Y.%m.%d-%H.%M.%S', time.localtime()) + '.log', print=True, write=False)

    # initialize graphs and people
    points, root = initialize()
    log.log(f"{len(points)} {count_graph_n(root)}", 'i')
    log.log_graph(root)

    # add test centers to medical zones
    test_centers = []
    classes = Location.separate_into_classes(root)
    for mz in classes[MedicalZone]:
        test_center = TestCenter(mz.x, mz.y, mz.radius)
        test_centers.append(test_center)

    # find cemeteries
    cemetery = classes[Cemetery]

    # initialize plots
    if PLOT:
        fig, ax, sc, hm = init_figure(root, points, test_centers, args.H, args.W, 0)
        fig2, axs = plt.subplots(2, 4)

    # initial iterations to initialize positions of the people
    for t in range(5):
        print(f"initializing {t}")
        root.process_people_movement(0)

    # main iteration loop
    for t in range(iterations):
        log.log(f"Iteration: {t} {i_to_time(t)}", 'w')
        log.log_people(points)

        # process movement
        root.process_people_movement(t)

        # process transmission and recovery
        disease_transmission(points, t)
        CovEngine.process_recovery(points, t)
        CovEngine.process_death(points, t, cemetery)

        # process testing
        if t % testing_freq == 0:
            testing_procedure(points, test_centers, t)

        # change routes randomly for some people
        for p in points:
            if (
                    p.is_infected() and p.is_tested_positive()) or p.is_dead():  # these people cant change route randomly!!!
                continue
            if np.random.rand() < 0.001:
                p.update_route(root, t % DAY, get_alternate_route(p))

        # spawn new test centers
        if t % test_center_spawn_check_freq == 0:
            test_center = TestCenter.spawn_test_center(test_center_spawn_method, points, test_centers, args.H,
                                                       args.W, args.test_center_r, test_center_spawn_threshold)
            if test_center is not None:
                print(f"Added new TEST CENTER at {test_center.x} {test_center.y}")
                test_centers.append(test_center)

        # check locations for any changes to quarantine state
        ContainmentEngine.check_locations(root, t)

        update_point_parameters(points)

        # overriding routes if necessary. (tested positives, etc)
        for p in points:
            if ContainmentEngine.check_to_update_route(p, root, args.containment, t):
                break

        # reset day

        if t % DAY == 0:
            for p in points:
                p.reset_day(t)

        # ==================================== plotting ==============================================================
        if PLOT:
            if t % 100 == 0:
                fig, ax, sc, hm = init_figure(root, points, test_centers, args.H, args.W, t)
                # update_figure(fig, ax, sc, hm, root, points, test_centers, args.H, args.W, t)
                plot_info(fig2, axs, points)

        # move_points(test_centers)


if __name__ == "__main__":
    main()
