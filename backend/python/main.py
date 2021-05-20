import numpy as np
import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import seaborn as sns

from backend.python.TransmissionEngine import TransmissionEngine
from backend.python.Visualizer import init_figure, update_figure, plot_info
from backend.python.enums import Mobility, Shape, State, TestSpawn
from backend.python.functions import bs
from backend.python.location.Town import Town
from backend.python.location.Building import Building
from backend.python.location.Location import Location
from backend.python.location.Institute import Institute
from backend.python.point.Point import Point
from backend.python.MovementEngine import MovementEngine
from backend.python.TestCenter import TestCenter
from backend.python.transport.Transport import Transport

"""
TODO: 

Make movement probability function
Infection using contagious areas
containment - moving positive patients to confined area and isolation
"""
parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
parser.add_argument('-n', help='target population', default=10000)
parser.add_argument('-H', help='height', type=int, default=102)
parser.add_argument('-W', help='width', type=int, default=102)
parser.add_argument('-i', help='initial infected', type=int, default=5)

parser.add_argument('--infect_r', help='infection radius', type=float, default=1)
parser.add_argument('--beta', help='transmission probability', type=float, default=0.1)
parser.add_argument('--gamma', help='recovery rate', type=float, default=1 / 14 / 10)
parser.add_argument('--common_p', help='common fever probability', type=float, default=0.1)

parser.add_argument('--containment',
                    help='containment strategy used (0-None, 1-Complete Lockdown, 2-Isolation based on contact tracing)',
                    type=int, default=0)
parser.add_argument('--testing', help='testing strategy used (0-Random, 1-Temperature based)', type=int, default=1)
parser.add_argument('--test_centers', help='Number of test centers', type=int, default=3)
parser.add_argument('--test_acc', help='Test accuracy', type=float, default=0.80)
parser.add_argument('--test_center_r', help='Mean radius of coverage from the test center', type=int, default=20)
parser.add_argument('--asymptotic_t', help='Mean asymptotic period. (Test acc gradually increases with disease age)',
                    type=int, default=14)

parser.add_argument('--initialize',
                    help='How to initialize the positions (0-Random, 1-From file 2-From probability map)', type=int,
                    default=0)

args = parser.parse_args()


def initialize_graph():
    vertex_data = [
        {'x': 0, 'y': 0, 'vcap': 8, 'exitx': 0, 'exity': 0, 'name': 'Kandy',
         'type': Shape.POLYGON.value, 'b': [(-100, -100), (100, -100), (100, 100), (-100, 100)],
         'class': Town},
        {'x': -70, 'y': -50, 'vcap': 8, 'exitx': -70, 'exity': -50, 'name': 'Residential',
         'type': Shape.CIRCLE.value, 'r': 30, 'class': Institute},
        {'x': 80, 'y': -10, 'vcap': 5, 'exitx': 70, 'exity': -5, 'name': 'Teaching',
         'type': Shape.CIRCLE.value, 'r': 20, 'class': Institute},
        {'x': 10, 'y': 70, 'vcap': 10, 'exitx': 0, 'exity': 60, 'name': 'Commercial-1',
         'type': Shape.CIRCLE.value, 'r': 20, 'class': Institute},
        {'x': 0, 'y': 0, 'vcap': 4, 'exitx': -5, 'exity': -5, 'name': 'Commercial-2',
         'type': Shape.CIRCLE.value, 'r': 25, 'class': Institute},
        {'x': -90, 'y': -50, 'vcap': 40, 'exitx': -90, 'exity': -40, 'name': 'H1',
         'type': Shape.CIRCLE.value, 'r': 10, 'class': Building},
        {'x': -55, 'y': -35, 'vcap': 4, 'exitx': -60, 'exity': -40, 'name': 'H2',
         'type': Shape.POLYGON.value, 'b': [(-70, -20), (-80, -80), (-60, -50)], 'class': Building},

    ]

    vertices = []
    for idx, v in enumerate(vertex_data):
        vertices.append(v['class'](idx, v['x'], v['y'], v['type'], v['exitx'], v['exity'], v['name']))
        if v['type'] == Shape.CIRCLE.value:
            vertices[-1].set_radius(v['r'])
        elif v['type'] == Shape.POLYGON.value:
            vertices[-1].set_boundary(v['b'])

        # root.add_sub_location(vertices[-1])
        # if v['leaf']:
        #     provinces[-1].override_transport = Transport(v['vcap'], Mobility.RANDOM.value)
        #     leaves.append(provinces[-1])
    connectivity = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (1, 6)]
    for a, b in connectivity:
        vertices[a].add_sub_location((vertices[b]))

    root = vertices[0]
    while root.parent_location is not None:
        root = root.parent_location

    leaves = []

    def dfs(rr: Location):
        if len(rr.locations) == 0:
            leaves.append(rr)
        for child in rr.locations:
            dfs(child)

    dfs(root)

    for leaf in leaves:
        leaf.override_transport = Transport(vertex_data[leaf.ID]['vcap'], Mobility.RANDOM.value)

    return root, leaves


def initialize():
    h = args.H
    w = args.W

    n = args.n
    i = args.i

    # grid = [[[] for _ in range(w)] for _ in range(h)]

    if args.initialize == 0:  # Random
        points = [Point(np.random.randint(-w, w), np.random.randint(-h, h)) for _ in range(n)]
    elif args.initialize == 1:
        raise NotImplemented()
    elif args.initialize == 2:
        raise NotImplemented()
    else:
        raise NotImplemented()

    for _ in range(i):
        idx = np.random.randint(0, n)
        points[idx].set_infected(0, None, args.common_p)

    root, leaves = initialize_graph()

    main_trans = [Transport(np.random.randint(1, 50), Mobility.RANDOM.value) for _ in range(5)]

    for point in points:
        point.set_random_route(leaves, 0)
        point.main_trans = main_trans[np.random.randint(0, len(main_trans))]

    return points, root


def disease_transmission(points, t):
    x, y = np.array([p.x for p in points]), np.array([p.y for p in points])
    state = np.array([p.state for p in points])

    r = args.infect_r

    contacts, distance, sourceid = TransmissionEngine.get_close_contacts_and_distance(x, y, state, r)

    new_infected = TransmissionEngine.transmit_disease(points, contacts, distance, sourceid, args.beta, args.common_p,
                                                       t)

    print(f"""{new_infected}/{sum(contacts > 0)}/{int(sum(contacts))}/{sum(state == State.INFECTED.value)} 
    Infected/Unique/Contacts/Active""")


def update_point_parameters(points):
    for i in range(args.n):
        points[i].update_temp()


def process_recovery(points):
    for i in range(args.n):
        if points[i].state == State.INFECTED.value:
            if np.random.rand() < args.gamma:
                points[i].set_recovered()


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
        x_idx_l = bs(xs, test_centers[i].x - r) + 1

        y_idx_r = bs(ys, test_centers[i].y + r)
        y_idx_l = bs(ys, test_centers[i].y - r) + 1

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


iterations = 1000
testing_freq = 10
test_center_spawn_check_freq = 10
test_center_spawn_method = TestSpawn.HEATMAP.value
test_center_spawn_threshold = 100


def main():
    PLOT = True
    points, root = initialize()
    test_centers = []

    if PLOT:
        fig, ax, sc, hm, test_center_patches = init_figure(root, points, test_centers, args.H, args.W)
        fig2, axs = plt.subplots(2, 2)

    for i in range(-5, iterations):
        print(f"Iteration: {i}")

        root.process_point_movement(i)
        if i >= 0:  # for initialization
            disease_transmission(points, i)
            process_recovery(points)

            if i % testing_freq == 0:
                testing_procedure(points, test_centers, i)

            if i % test_center_spawn_check_freq == 0:
                test_center = TestCenter.spawn_test_center(test_center_spawn_method, points, test_centers, args.H,
                                                           args.W, args.test_center_r, test_center_spawn_threshold)
                if test_center is not None:
                    print(f"Added new TEST CENTER at {test_center.x} {test_center.y}")
                    test_centers.append(test_center)

            if PLOT:
                if i % 1 == 0:
                    update_figure(fig, ax, sc, hm, points, test_centers, test_center_patches, args.H, args.W)
                plot_info(fig2, axs, points)

        # move_points(test_centers)


if __name__ == "__main__":
    main()
