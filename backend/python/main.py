import numpy as np
import argparse
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import seaborn as sns

from functions import bs
from Point import Point
from MovementEngine import MovementEngine
from TestCenter import TestCenter

"""
TODO: 

Make movement probability function
Infection using contagious areas
containment - moving positive patients to confined area and isolation
"""
iterations = 1000
default_pop = 1000
parser = argparse.ArgumentParser(description='Create emulator for COVID-19 pandemic')
parser.add_argument('-n', help='target population', default=default_pop)
parser.add_argument('-H', help='height', type=int, default=320)
parser.add_argument('-W', help='width', type=int, default=320)
parser.add_argument('-i', help='initial infected', type=int, default=5)

parser.add_argument('--infect_r', help='infection radius', type=float, default=5.0)
parser.add_argument('--beta', help='transmission probability', type=float, default=0.3)
parser.add_argument('--gamma', help='recovery rate', type=float, default=0.01)
parser.add_argument('--common_p', help='common fever probability', type=float, default=0.1)

parser.add_argument('--containment',
                    help='containment strategy used (0-None, 1-Complete Lockdown, 2-Isolation based on contact tracing)',
                    type=int, default=0)
parser.add_argument('--testing', help='testing strategy used (0-Random, 1-Temperature based)', type=int, default=1)
parser.add_argument('--test_centers', help='Number of test centers', type=int, default=10)
parser.add_argument('--test_acc', help='Test accuracy', type=float, default=0.80)
parser.add_argument('--test_center_r', help='Mean radius of coverage from the test center', type=int, default=50)
parser.add_argument('--asymptotic_t', help='Mean asymptotic period. (Test acc gradually increases with disease age)',
                    type=int, default=14)

parser.add_argument('--initialize',
                    help='How to initialize the positions (0-Random, 1-From file 2-From probability map)', type=int,
                    default=0)

parser.add_argument('--mobility', help='How people move around (0-Random, 1-Brownian)', type=int, default=0)
parser.add_argument('--mobility_r', help='mobility radius', type=int, default=10)

args = parser.parse_args()


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
        points[idx].set_infected(0, args.common_p)

    test_centers = [TestCenter(np.random.randint(-w, w),
                               np.random.randint(-h, h),
                               np.random.normal(args.test_center_r, 10)
                               ) for _ in range(args.test_centers)]

    return points, test_centers


def init_figure(points, test_centers):
    fig = plt.figure(1)
    x, y = [p.x for p in points], [p.y for p in points]
    sc = plt.scatter(x, y)
    ax = plt.gca()
    for test in test_centers:
        circle = plt.Circle((test.x, test.y), test.r, color='b', fill=False)
        ax.add_patch(circle)
    plt.xlim(-args.W, args.W)
    plt.ylim(-args.H, args.H)
    plt.draw()
    return fig, ax, sc


def update_figure(fig, ax, sc, points, test_centers):
    x, y = [p.x for p in points], [p.y for p in points]
    s = np.array([p.state for p in points])
    s = (-s * 128 + 128)
    v = [(p.vx ** 2 + p.vy ** 2) ** 0.5 + 1 for p in points]

    # n = mpl.colors.Normalize(vmin=min(s), vmax=max(s))
    # m = mpl.cm.ScalarMappable( cmap=plt.get_cmap('brg'))
    sc.set_facecolor(plt.get_cmap('brg')(s))
    sc.set_clim(vmin=-1, vmax=1)

    sc._sizes = [1 for _ in points]  # v

    sc.set_offsets(np.c_[x, y])

    for i, test in enumerate(test_centers):
        ax.patches[i].center = test.x, test.y

    fig.canvas.draw_idle()
    plt.pause(0.01)


def move_points(points):
    for i in range(len(points)):
        MovementEngine.move(points[i], args)


def disease_transmission(points, t):
    x, y = [p.x for p in points], [p.y for p in points]
    xs = np.sort(x)
    ys = np.sort(y)
    xs_idx = np.argsort(x)
    ys_idx = np.argsort(y)

    for i in range(len(points)):  # iterate through infected people only to increase speed
        if points[i].state != 1:
            continue

        # infect to closest points
        r = args.infect_r

        x_idx_r = bs(xs, points[i].x + r)
        x_idx_l = bs(xs, points[i].x - r) + 1

        y_idx_r = bs(ys, points[i].y + r)
        y_idx_l = bs(ys, points[i].y - r) + 1

        close_points = np.intersect1d(xs_idx[x_idx_l:x_idx_r], ys_idx[y_idx_l:y_idx_r])
        for p_idx in close_points:
            if points[p_idx].state == 0:
                points[p_idx].transmit_disease(points[i], args.beta, args.common_p, t)


def update_point_parameters(points):
    for i in range(args.n):
        points[i].update_temp()


def process_recovery(points):
    for i in range(args.n):
        if points[i].state == 1:
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


def gather_info(points):
    s, i, r = 0, 0, 0
    temps = [p.temp for p in points]
    for p in points:
        if p.state == -1:
            r += 1
        elif p.state == 0:
            s += 1
        elif p.state == 1:
            i += 1
    return {"S": s, "I": i, "R": r, "Temp-mean": np.mean(temps), "Temp-std": np.std(temps)}


def plot_info(fig, axs, points):
    temps = [p.temp for p in points]
    state = [p.state for p in points]

    df = pd.DataFrame({"Temp": temps, "State": state})

    axs[0, 0].cla()
    sns.histplot(df, x="Temp", hue="State", ax=axs[0, 0])

    ax = axs[0, 1]
    s, i, r = sum(df["State"] == 0), sum(df["State"] == 1), sum(df["State"] == -1)
    if len(ax.lines) == 0:
        ax.plot([s])
        ax.plot([i])
        ax.plot([r])
    else:
        x, y = ax.lines[0].get_data()
        x, y = np.append(x, len(x)), np.append(y, s)
        ax.lines[0].set_xdata(x), ax.lines[0].set_ydata(y)

        x, y = ax.lines[1].get_data()
        x, y = np.append(x, len(x)), np.append(y, i)
        ax.lines[1].set_xdata(x), ax.lines[1].set_ydata(y)

        x, y = ax.lines[2].get_data()
        x, y = np.append(x, len(x)), np.append(y, r)
        ax.lines[2].set_xdata(x), ax.lines[2].set_ydata(y)

        ax.set_xlim(0, len(x))
        fig.canvas.draw(), fig.canvas.flush_events()

    ax = axs[1, 0]
    cum_positive = np.array([p.tested_positive_time for p in points])
    cum_positive = sum(cum_positive >= 0)
    daily_positive = cum_positive
    if len(ax.lines) == 0:
        ax.plot([cum_positive])
    else:
        x, y = ax.lines[0].get_data()
        daily_positive = cum_positive - y[-1]
        x, y = np.append(x, len(x)), np.append(y, cum_positive)
        ax.lines[0].set_xdata(x), ax.lines[0].set_ydata(y)
        ax.set_xlim(0, len(x))
        ax.set_ylim(0, max(y) + 10)
        fig.canvas.draw(), fig.canvas.flush_events()

    ax = axs[1, 1]
    if len(ax.lines) == 0:
        ax.plot([daily_positive])
    else:
        x, y = ax.lines[0].get_data()
        x, y = np.append(x, len(x)), np.append(y, daily_positive)
        ax.lines[0].set_xdata(x), ax.lines[0].set_ydata(y)
        ax.set_xlim(0, len(x))
        ax.set_ylim(0, max(y) + 10)
        fig.canvas.draw(), fig.canvas.flush_events()


def main():
    points, test_centers = initialize()
    fig, ax, sc = init_figure(points, test_centers)
    fig2, axs = plt.subplots(2, 2)

    for i in range(iterations):
        print(f"Iteration: {i}")

        move_points(points)

        disease_transmission(points, i)

        process_recovery(points)

        # move_points(test_centers)

        if i % 10 == 0:
            plot_info(fig2, axs, points)
            testing_procedure(points, test_centers, i)
        update_figure(fig, ax, sc, points, test_centers)


if __name__ == "__main__":
    main()
