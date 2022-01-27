import numpy as np

from backend.python.Logger import Logger
from backend.python.enums import State, PersonFeatures
from backend.python.transport import Walk, Bus
from backend.python.transport.CommercialZoneBus import CommercialZoneBus
from backend.python.transport.SchoolBus import SchoolBus
from backend.python.transport.Tuktuk import Tuktuk


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
    def get_heatmap(points, h, w):
        res = 50
        yy, xx = np.meshgrid(np.linspace(-h, h, res), np.linspace(-w, w, res))
        zz = np.zeros_like(xx)
        dw, dh = (2 * w + 1) / res, (2 * h + 1) / res
        for p in points:
            if p.state == State.INFECTED.value:
                x = p.features[p.ID, PersonFeatures.px.value]
                y = p.features[p.ID, PersonFeatures.py.value]
                if x > w or y > h:
                    Logger.log("Person outside map", 'c')
                    continue
                try:
                    zz[int(x // dw) + res // 2, int(y // dh) + res // 2] += 1  # todo bugsy
                except IndexError as e:
                    Logger.log(str(e), 'c')
        return xx, yy, zz

