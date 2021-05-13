import numpy as np
import argparse
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib as mpl
import pandas as pd
import seaborn as sns
from numba import jit, njit

from backend.python.enums import Mobility, Shape, State
from backend.python.functions import bs
from backend.python.location.Country import Country
from backend.python.location.District import District
from backend.python.location.Location import Location
from backend.python.location.Province import Province
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
iterations = 1000
default_pop = 10000
parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
parser.add_argument('-n', help='target population', default=default_pop)
parser.add_argument('-H', help='height', type=int, default=102)
parser.add_argument('-W', help='width', type=int, default=102)
parser.add_argument('-i', help='initial infected', type=int, default=5)

parser.add_argument('--infect_r', help='infection radius', type=float, default=1)
parser.add_argument('--beta', help='transmission probability', type=float, default=0.1)
parser.add_argument('--gamma', help='recovery rate', type=float, default=1 / 14 /10)
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

parser.add_argument('--mobility', help='How people move around (0-Random, 1-Brownian)', type=int, default=0)
parser.add_argument('--mobility_r', help='mobility radius', type=int, default=10)

args = parser.parse_args()


def initialize_graph():
    vertex_data = [
        {'x': 0, 'y': 0, 'vcap': 80, 'exitx': 0, 'exity': 0, 'name': 'Sri Lanka',
         'type': Shape.POLYGON.value, 'b': [(-100, -100), (100, -100), (100, 100), (-100, 100)],
         'class': Country},
        {'x': -70, 'y': -50, 'vcap': 80, 'exitx': -70, 'exity': -50, 'name': 'Western',
         'type': Shape.CIRCLE.value, 'r': 30, 'class': Province},
        {'x': 80, 'y': -10, 'vcap': 50, 'exitx': 70, 'exity': -5, 'name': 'Eastern',
         'type': Shape.CIRCLE.value, 'r': 20, 'class': Province},
        {'x': 10, 'y': 70, 'vcap': 100, 'exitx': 0, 'exity': 50, 'name': 'North',
         'type': Shape.CIRCLE.value, 'r': 20, 'class': Province},
        {'x': 0, 'y': 0, 'vcap': 40, 'exitx': -5, 'exity': -5, 'name': 'Central',
         'type': Shape.CIRCLE.value, 'r': 25, 'class': Province},
        {'x': -70, 'y': -50, 'vcap': 40, 'exitx': -80, 'exity': -40, 'name': 'Colombo',
         'type': Shape.POLYGON.value, 'b': [(-85, -40), (-75, -40), (-75, -55), (-85, -55)], 'class': District},
        {'x': -55, 'y': -35, 'vcap': 40, 'exitx': -60, 'exity': -40, 'name': 'Gampaha',
         'type': Shape.POLYGON.value, 'b': [(-70, -20), (-80, -80), (-60, -50)], 'class': District},

    ]

    leaves = []
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

    test_centers = [TestCenter(np.random.randint(-w, w),
                               np.random.randint(-h, h),
                               np.random.normal(args.test_center_r, 2)
                               ) for _ in range(args.test_centers)]
    root, leaves = initialize_graph()

    main_trans = [Transport(np.random.randint(1, 50), Mobility.RANDOM.value) for _ in range(5)]

    for point in points:
        route = [leaves[np.random.randint(0, len(leaves))] for _ in range(np.random.randint(2, 5))]
        duration = [np.random.randint(10, 200) for _ in range(len(route))]
        point.x = route[0].x + np.random.normal(0, 10)
        point.y = route[0].y + np.random.normal(0, 10)
        route[0].add_point(point, 0)
        point.set_route(route, duration)
        point.main_trans = main_trans[np.random.randint(0, len(main_trans))]

    return points, test_centers, root


point_colors = {State.SUSCEPTIBLE.value: 'b', State.INFECTED.value: 'r', State.RECOVERED.value: 'g'}
point_names = {State.SUSCEPTIBLE.value: State.SUSCEPTIBLE.name,
               State.INFECTED.value: State.INFECTED.name,
               State.RECOVERED.value: State.RECOVERED.name}


def init_figure(root, points, test_centers):
    h, w = args.H, args.W

    # drawing points and test centers
    fig = plt.figure(1)
    ax = plt.gca()
    x, y = [p.x for p in points], [p.y for p in points]
    sc = plt.scatter(x, y)
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label=point_names[key], markerfacecolor=point_colors[key],
               markersize=15) for key in point_colors.keys()
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    for test in test_centers:
        circle = plt.Circle((test.x, test.y), test.r, color='b', fill=False)
        ax.add_patch(circle)

    # drawing heatmap
    res = 20
    xx, yy = np.meshgrid(np.linspace(-h, h, res), np.linspace(-w, w, res))
    zz = np.zeros_like(xx)
    dw, dh = (2 * w + 1) / res, (2 * h + 1) / res
    for p in points:
        if p.state == State.INFECTED.value:
            zz[int(p.x // dw) + res // 2, int(p.y // dh) + res // 2] += 1
    # zz = zz[:-1, :-1]
    hm = ax.pcolormesh(xx, yy, zz, cmap='Reds', shading='auto', alpha=0.5)
    fig.colorbar(hm, ax=ax)

    def dfs(rr: Location):
        if rr.shape == Shape.CIRCLE.value:
            circle = plt.Circle((rr.x, rr.y), rr.radius, color='g', fill=False)
            ax.add_patch(circle)
        elif rr.shape == Shape.POLYGON.value:
            coord = rr.boundary
            coord.append(coord[0])  # repeat the first point to create a 'closed loop'
            xs, ys = zip(*coord)  # create lists of x and y values
            ax.plot(xs, ys)

        for child in rr.locations:
            dfs(child)

    dfs(root)

    plt.xlim(-w, w)
    plt.ylim(-h, h)
    plt.draw()
    return fig, ax, sc, hm


def update_figure(fig, ax, sc, hm, points, test_centers):
    h, w = args.H, args.W

    x, y = [p.x for p in points], [p.y for p in points]

    sc.set_facecolor([point_colors[p.state] for p in points])
    # s = np.array([p.state for p in points])
    # s = (s * 256 / 3)
    # sc.set_facecolor(plt.get_cmap('brg')(s))

    v = [(p.vx ** 2 + p.vy ** 2) ** 0.5 + 1 for p in points]

    # sc.set_clim(vmin=0, vmax=2)

    sc._sizes = [1 for _ in points]  # v

    sc.set_offsets(np.c_[x, y])

    for i, test in enumerate(test_centers):
        ax.patches[i].center = test.x, test.y

    res = 20
    yy, xx = np.meshgrid(np.linspace(-h, h, res), np.linspace(-w, w, res))
    zz = np.zeros_like(xx)
    dw, dh = (2 * w + 1) / res, (2 * h + 1) / res
    for p in points:
        if p.state == State.INFECTED.value:
            zz[int(p.y // dh) + res // 2, int(p.x // dw) + res // 2] += 1
    # zz = zz[:-1, :-1]
    hm.set_array(zz.ravel())

    cbar = hm.colorbar
    vmax = max(cbar.vmax, np.max(zz))
    hm.set_clim(0, vmax)
    cbar_ticks = np.linspace(0., vmax, num=10, endpoint=True)
    cbar.set_ticks(cbar_ticks)
    cbar.draw_all()

    fig.canvas.draw_idle()
    plt.pause(0.01)


def disease_transmission(points, t):
    x, y = np.array([p.x for p in points]), np.array([p.y for p in points])
    # change this to distance and do it

    r = args.infect_r

    xs = np.sort(x)
    ys = np.sort(y)
    xs_idx = np.argsort(x)
    ys_idx = np.argsort(y)
    new_infected = 0
    close_contacts = 0
    active = 0
    for i in range(len(points)):
        # iterate through infected people only to increase speed
        if points[i].state != State.INFECTED.value:
            continue
        active += 1
        # infect to closest points

        x_idx_r = bs(xs, points[i].x + r)
        x_idx_l = bs(xs, points[i].x - r)

        y_idx_r = bs(ys, points[i].y + r)
        y_idx_l = bs(ys, points[i].y - r)

        close_points = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r])
        for p_idx in close_points:
            if points[p_idx].state == State.SUSCEPTIBLE.value:
                d2 = (points[p_idx].x - points[i].x) ** 2 + (points[p_idx].y - points[i].y) ** 2
                d = np.sqrt(d2)
                if d < r:
                    close_contacts += 1
                    is_infected = points[p_idx].transmit_disease(points[i], args.beta, args.common_p, d, t)
                    if is_infected:
                        new_infected += 1
    print(f"{new_infected}/{close_contacts}/{active} Infected/Close/Active")


def update_point_parameters(points):
    for i in range(args.n):
        points[i].update_temp()


def process_recovery(points):
    for i in range(args.n):
        if points[i].state == State.INFECTED.value:
            if np.random.rand() < args.gamma:
                points[i].set_recovered()


def testing_procedure(points, test_centers, t):
    x, y = [p.x for p in points], [p.y for p in points]
    xs = np.sort(x)
    ys = np.sort(y)
    xs_idx = np.argsort(x)
    ys_idx = np.argsort(y)

    test_subjects = set()

    for i in range(len(test_centers)):  # iterate through test centers

        r = test_centers[i].r

        x_idx_r = bs(xs, test_centers[i].x + r)
        x_idx_l = bs(xs, test_centers[i].x - r) + 1

        y_idx_r = bs(ys, test_centers[i].y + r)
        y_idx_l = bs(ys, test_centers[i].y - r) + 1

        close_points = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r])
        for close_point in close_points:
            test_subjects.add(close_point)
    for p_idx in test_subjects:
        TestCenter.test(points[p_idx], t, args)


def add_to_line(ax, line_no, data, delta=False):
    x, y = ax.lines[line_no].get_data()
    if delta:
        data = y[-1] + data
    x, y = np.append(x, len(x)), np.append(y, data)
    ax.lines[line_no].set_xdata(x), ax.lines[line_no].set_ydata(y)
    return y


def plot_info(fig, axs, points):
    temps = [p.temp for p in points]
    state = [p.state for p in points]

    df = pd.DataFrame({"Temp": temps, "State": state})

    axs[0, 0].cla()
    sns.histplot(df, x="Temp", hue="State", ax=axs[0, 0])

    ax = axs[0, 1]
    s, i, r = sum(df["State"] == State.SUSCEPTIBLE.value), sum(df["State"] == State.INFECTED.value), sum(
        df["State"] == State.RECOVERED.value)
    if len(ax.lines) == 0:
        ax.plot([s])
        ax.plot([i])
        ax.plot([r])
        ax.legend(["S", "I", "R"])
        y_s = s
        y_i = i
        y_r = r

    else:
        max_value = 0

        y = add_to_line(ax, 0, s)
        y_s = y[-2]
        max_value = max(max_value, max(y))

        y = add_to_line(ax, 1, i)
        y_i = y[-2]
        max_value = max(max_value, max(y))

        y = add_to_line(ax, 2, r)
        y_r = y[-2]
        max_value = max(max_value, max(y))

        ax.set_xlim(0, len(y))
        ax.set_ylim(0, max_value + 2)
        fig.canvas.draw(), fig.canvas.flush_events()

    ax = axs[1, 0]
    cum_positive = np.array([p.tested_positive_time for p in points])
    cum_positive = sum(cum_positive >= 0)
    cum_r = r
    if len(ax.lines) == 0:
        daily_positive = cum_positive
        daily_new = i
        daily_r = r
        ax.plot([cum_positive])
        ax.plot([i])
        ax.plot([cum_r])
        ax.legend(["Cumulative tested positive", "Cumulative true positive","Cumulative recovered"])

    else:
        max_value = 0
        y = add_to_line(ax, 0, cum_positive)
        daily_positive = y[-1] - y[-2]
        daily_r = r - y_r
        max_value = max(max_value, max(y))

        daily_new = i - y_i + daily_r
        y = add_to_line(ax, 1, daily_new, delta=True)
        max_value = max(max_value, max(y))

        y = add_to_line(ax, 2, daily_r, delta=True)
        max_value = max(max_value, max(y))

        ax.set_xlim(0, len(y))
        ax.set_ylim(0, max_value + 2)
        fig.canvas.draw(), fig.canvas.flush_events()

    ax = axs[1, 1]
    if len(ax.lines) == 0:
        ax.plot([daily_positive])
        ax.plot([daily_new])
        ax.plot([daily_r])
        ax.legend(["Daily tested positive", "Daily true positive","Daily recovered"])
    else:
        max_value = 0
        y = add_to_line(ax, 0, daily_positive)
        max_value = max(max_value, max(y))

        y = add_to_line(ax, 1, daily_new)
        max_value = max(max_value, max(y))

        y = add_to_line(ax, 2, daily_r)
        max_value = max(max_value, max(y))

        ax.set_xlim(0, len(y))
        ax.set_ylim(0, max_value + 2)
        fig.canvas.draw(), fig.canvas.flush_events()


def main():
    points, test_centers, root = initialize()
    fig, ax, sc, hm = init_figure(root, points, test_centers)
    fig2, axs = plt.subplots(2, 2)

    for i in range(-5, iterations):
        print(f"Iteration: {i}")

        root.process_point_movement(i)
        if i >=0:  # for initialization
            disease_transmission(points, i)
            process_recovery(points)
            if i % 10 == 0:
                testing_procedure(points, test_centers, i)
                update_figure(fig, ax, sc, hm, points, test_centers)

            plot_info(fig2, axs, points)

        # move_points(test_centers)


if __name__ == "__main__":
    main()
