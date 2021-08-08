import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.lines import Line2D

from backend.python.Logger import Logger

from backend.python.Time import Time
from backend.python.location.Location import Location

from backend.python.enums import Mobility, Shape, State
from backend.python.point.Transporter import Transporter
from backend.python.transport import Walk, Bus
from backend.python.transport.CommercialZoneBus import CommercialZoneBus
from backend.python.transport.SchoolBus import SchoolBus
from backend.python.transport.Tuktuk import Tuktuk

import matplotlib.dates as mdates


class Visualizer:
    point_colors = {State.SUSCEPTIBLE.value: 'b',
                    State.INFECTED.value: 'r',
                    State.RECOVERED.value: 'g',
                    State.DEAD.value: 'k'}

    point_edgecolors = {Bus.__name__.split('.')[-1]: [0, 1, 1, 0.1],
                        CommercialZoneBus.__name__.split('.')[-1]: [0, 0.5, 1, 0.1],
                        Tuktuk.__name__.split('.')[-1]: [0.5, 0, 1, 0.1],
                        Walk.__name__.split('.')[-1]: [1, 0, 1, 0.1],
                        SchoolBus.__name__.split('.')[-1]: [0.5, 0.5, 0, 0.1]}

    point_names = {State.SUSCEPTIBLE.value: State.SUSCEPTIBLE.name,
                   State.INFECTED.value: State.INFECTED.name,
                   State.RECOVERED.value: State.RECOVERED.name,
                   State.DEAD.value: State.DEAD.name}
    test_center_color = 'yellow'
    location_palette = {}
    loc_cls2id = {}

    info_fig = None
    info_axs = []

    map_fig = None
    map_ax = None
    hm = None
    sc = None

    timeline_fig = None
    timeline_axs = []
    scale = 1000

    @staticmethod
    def initialize(root, test_centers, points,loc_class_map, h, w):
        Visualizer.init_location_colors(loc_class_map)
        Visualizer.init_map_figure(root, test_centers, points, h, w)
        Visualizer.init_info_figure()
        Visualizer.init_timeline_figure()

    @staticmethod
    def init_map_figure(root, test_centers, points, h, w):
        Visualizer.map_fig, Visualizer.map_ax = plt.subplots(figsize=(8, 8))

        # drawing heat-map
        xx, yy, zz = Visualizer.get_heatmap(points, h, w)
        Visualizer.hm = Visualizer.map_ax.pcolormesh(xx / Visualizer.scale, yy / Visualizer.scale, zz,
                                                     cmap='Reds', shading='auto', alpha=0.9)
        Visualizer.map_fig.colorbar(Visualizer.hm, ax=Visualizer.map_ax)

        Visualizer.map_ax.annotate(Time.i_to_time(0), (-w / Visualizer.scale, h / Visualizer.scale),
                                   xytext=(-w / Visualizer.scale, h / Visualizer.scale), fontsize=7)

        # drawing points
        p = points[0]
        x, y = p.all_positions[:, 0] / Visualizer.scale, p.all_positions[:, 1] / Visualizer.scale
        if len(points) > 10000:
            x, y = [], []
        Visualizer.sc = Visualizer.map_ax.scatter(x, y, alpha=0.8, s=5)

        Visualizer.draw_map(root, test_centers, update=False)
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label=Visualizer.point_names[key],
                   markerfacecolor=Visualizer.point_colors[key],
                   markersize=5) for key in Visualizer.point_colors.keys()
        ]
        Visualizer.map_ax.legend(handles=legend_elements, loc='upper right')

        Visualizer.map_ax.set_xlim(-w / Visualizer.scale, w / Visualizer.scale)
        Visualizer.map_ax.set_ylim(-h / Visualizer.scale, h / Visualizer.scale)

    @staticmethod
    def init_info_figure():
        fig, axs = plt.subplots(2, 3)
        Visualizer.info_fig = fig
        Visualizer.info_axs = axs

    @staticmethod
    def init_timeline_figure():
        # ======================================================================= plot line plot
        fig, axs = plt.subplots(1, 3, figsize=(15, 6))
        Visualizer.timeline_fig = fig
        Visualizer.timeline_axs = axs

    @staticmethod
    def init_location_colors(loc_class_map):
        # ====================================================== find all the class names and creates color palette
        cmap = sns.color_palette("Spectral", as_cmap=True)

        palette = {}
        for i, cls in enumerate(loc_class_map.keys()):
            cc = i / len(loc_class_map)
            palette[i] = cmap(cc)
        Visualizer.loc_cls2id = loc_class_map
        Visualizer.location_palette = palette

    @staticmethod
    def add_to_line(ax, line_no, data, delta=False):
        x, y = ax.lines[line_no].get_data()
        if delta:
            data = y[-1] + data
        x, y = np.append(x, len(x)), np.append(y, data)
        ax.lines[line_no].set_xdata(x), ax.lines[line_no].set_ydata(y)
        return y

    @staticmethod
    def plot_info(points):
        temps = [p.temp for p in points]
        state = [p.state for p in points]

        df = pd.DataFrame({"Temp": temps, "State": state})

        # ============================================================================================= S I R plot
        Visualizer.info_axs[0][0].cla()
        sns.histplot(df, x="Temp", hue="State", ax=Visualizer.info_axs[0][0])

        ax = Visualizer.info_axs[0][1]
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

            y = Visualizer.add_to_line(ax, 0, s)
            y_s = y[-2]
            max_value = max(max_value, max(y))

            y = Visualizer.add_to_line(ax, 1, i)
            y_i = y[-2]
            max_value = max(max_value, max(y))

            y = Visualizer.add_to_line(ax, 2, r)
            y_r = y[-2]
            max_value = max(max_value, max(y))

            ax.set_xlim(0, len(y))
            ax.set_ylim(0, max_value + 2)
            Visualizer.info_fig.canvas.draw(), Visualizer.info_fig.canvas.flush_events()

        # ========================================================================================= Cumulative plots
        ax = Visualizer.info_axs[1][0]
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
            ax.legend(["Cumulative tested positive", "Cumulative true positive", "Cumulative recovered"])
        else:
            max_value = 0
            y = Visualizer.add_to_line(ax, 0, cum_positive)
            daily_positive = y[-1] - y[-2]
            daily_r = r - y_r
            max_value = max(max_value, max(y))

            daily_new = i - y_i + daily_r
            y = Visualizer.add_to_line(ax, 1, daily_new, delta=True)
            max_value = max(max_value, max(y))

            y = Visualizer.add_to_line(ax, 2, daily_r, delta=True)
            max_value = max(max_value, max(y))

            ax.set_xlim(0, len(y))
            ax.set_ylim(0, max_value + 2)
            Visualizer.info_fig.canvas.draw(), Visualizer.info_fig.canvas.flush_events()

        # ========================================================================================= Daily plots
        ax = Visualizer.info_axs[1][1]
        if len(ax.lines) == 0:
            ax.plot([daily_positive])
            ax.plot([daily_new])
            ax.plot([daily_r])
            ax.legend(["Daily tested positive", "Daily true positive", "Daily recovered"])
        else:
            max_value = 0
            y = Visualizer.add_to_line(ax, 0, daily_positive)
            max_value = max(max_value, max(y))

            y = Visualizer.add_to_line(ax, 1, daily_new)
            max_value = max(max_value, max(y))

            y = Visualizer.add_to_line(ax, 2, daily_r)
            max_value = max(max_value, max(y))

            ax.set_xlim(0, len(y))
            ax.set_ylim(0, max_value + 2)
            Visualizer.info_fig.canvas.draw(), Visualizer.info_fig.canvas.flush_events()

    @staticmethod
    def plot_map_and_points(root, points, test_centers, h, w, t):
        Visualizer.map_ax.texts[0]._text = Time.i_to_time(t)
        if len(points) <= 10000:
            p = points[0]
            x, y = p.all_positions[:, 0] / Visualizer.scale, p.all_positions[:, 1] / Visualizer.scale

            Visualizer.sc.set_facecolor([Visualizer.point_colors[p.state] for p in points])
            Visualizer.sc.set_edgecolor(
                [Visualizer.point_edgecolors[p.current_trans.__class__.__name__] for p in points])
            Visualizer.sc.set_linewidth([2 for _ in points])
            Visualizer.sc._sizes = [40 + 2 * len(p.latched_people) if isinstance(p, Transporter) else 20 for p in
                                    points]
            Visualizer.sc.set_offsets(np.c_[x, y])

        Visualizer.map_ax.patches = []
        Visualizer.draw_map(root, test_centers, update=True)

        xx, yy, zz = Visualizer.get_heatmap(points, h, w)
        Visualizer.hm.set_array(zz.ravel())

        cbar = Visualizer.hm.colorbar
        vmax = max(cbar.vmax, np.max(zz))
        Visualizer.hm.set_clim(0, vmax)
        cbar_ticks = np.linspace(0., vmax, num=10, endpoint=True)
        cbar.set_ticks(cbar_ticks)
        cbar.draw_all()

        Visualizer.map_fig.canvas.draw_idle()

    @staticmethod
    def draw_map(root, test_centers, update=False):
        # drawing test centers
        for test in test_centers:
            circle = plt.Circle((test.x / Visualizer.scale, test.y / Visualizer.scale),
                                test.r / Visualizer.scale, color=Visualizer.test_center_color,
                                fill=True,
                                alpha=0.3)
            Visualizer.map_ax.add_patch(circle)

        # drawing locations
        def dfs(rr: Location):
            if rr.shape == Shape.CIRCLE.value:
                circle = plt.Circle((rr.x / Visualizer.scale, rr.y / Visualizer.scale),
                                    rr.radius / Visualizer.scale, facecolor=[1, 0, 0, 0.5],
                                    fill=rr.quarantined,
                                    edgecolor=Visualizer.location_palette[Visualizer.loc_cls2id[rr.__class__.__name__]])
                Visualizer.map_ax.add_patch(circle)
            elif rr.shape == Shape.POLYGON.value:
                coord = rr.boundary
                coord = np.concatenate([coord, coord[0:1, :]],
                                       axis=0)  # repeat the first point to create a 'closed loop'
                xs, ys = coord[:, 0] / Visualizer.scale, coord[:,
                                                         1] / Visualizer.scale  # create lists of x and y values
                Visualizer.map_ax.plot(xs, ys)
            x = rr.exit[0] / Visualizer.scale
            y = rr.exit[1] / Visualizer.scale
            if not update:
                Visualizer.map_ax.scatter(x, y, marker='x', s=5)
            if rr.depth <= 2:
                if not update:
                    Visualizer.map_ax.annotate(rr.name, (x, y),
                                               xytext=(x + 10 / Visualizer.scale, y + 10 / Visualizer.scale),
                                               fontsize=7,
                                               arrowprops=dict(arrowstyle="->",
                                                               connectionstyle="angle3,angleA=0,angleB=-90"))
            for child in rr.locations:
                dfs(child)

        dfs(root)

    @staticmethod
    def get_heatmap(points, h, w):
        res = 50
        yy, xx = np.meshgrid(np.linspace(-h, h, res), np.linspace(-w, w, res))
        zz = np.zeros_like(xx)
        dw, dh = (2 * w + 1) / res, (2 * h + 1) / res
        for p in points:
            if p.state == State.INFECTED.value:
                if p.all_positions[p.ID, 0] > w or p.all_positions[p.ID, 1] > h:
                    Logger.log("Person outside map", 'c')
                    continue
                try:
                    zz[int(p.all_positions[p.ID, 0] // dw) + res // 2, int(
                        p.all_positions[p.ID, 1] // dh) + res // 2] += 1  # todo bugsy
                except IndexError as e:
                    Logger.log(str(e), 'c')
        return xx, yy, zz

    @staticmethod
    def plot_position_timeline(df, root):
        ax = Visualizer.timeline_axs[0]
        hm = ax.collections[-1] if len(ax.collections) > 0 else None
        g = df[['time', 'location']].groupby(['time', 'location'])
        g = g.size().reset_index(name='count')
        g = g.pivot(index='location', columns='time', values='count')
        g.fillna(0, inplace=True)

        if hm is not None:
            hm.colorbar.remove()
            plt.draw()
            ax.cla()
        hm = sns.heatmap(g, ax=ax, cbar=True, xticklabels=g.values.shape[1] // 10)
        xlabels = hm.get_xticklabels()
        for i in range(len(xlabels)):
            xlabels[i].set_text(xlabels[i].get_text()[:16])
        hm.set_xticklabels(xlabels)
        # ax.cla()
        # sns.lineplot(data=df, x='time', hue='person', y='location', ax=ax)

        # ax.tick_params(axis='x', which='major', rotation=90, labelsize=8, colors='r', pad=2)
        # ax.tick_params(axis='x', which='minor', rotation=90, labelsize=6, colors='b')

        # ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        # ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
        # ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(ax.xaxis.get_major_locator()))
        # ax.xaxis.set_minor_formatter(mdates.AutoDateFormatter(ax.xaxis.get_minor_locator()))

        # ax.xaxis.set_major_locator(mdates.DayLocator())
        # ax.xaxis.set_minor_locator(mdates.HourLocator())
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%D'))
        # ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M'))

        # ======================================================================= sets background color in line plot
        def f(r):
            Visualizer.timeline_axs[0].axhspan(r.ID - 0.49, r.ID + 0.49,
                                               color=Visualizer.location_palette[Visualizer.loc_cls2id[r.__class__.__name__]],
                                               alpha=0.5)
            for ch in r.locations:
                f(ch)

        # f(root)

        ax = Visualizer.timeline_axs[1]
        ax.cla()
        # df['day_time'] = pd.to_datetime((df['time'].apply(lambda x: x.value) % (1440 * 60 * 1e9)).astype('int64'))
        df['day_time'] = (df['time'] % 1440).astype('int64')
        sns.histplot(data=df, x='day_time', hue='loc_class', palette=Visualizer.location_palette, ax=ax)
        # ax.xaxis.set_tick_params(rotation=90)
        # ax.xaxis.set_major_locator(mdates.HourLocator())
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        ax = Visualizer.timeline_axs[2]
        ax.cla()
        df['per_complete'] = df['cur_tar_idx'] / (df['route_len'] - 1)

        sns.lineplot(data=df, x='day_time', y='per_complete', hue='person_class', ax=ax)
        # ax.xaxis.set_tick_params(rotation=90)
        # ax.xaxis.set_major_locator(mdates.HourLocator())
        # ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
