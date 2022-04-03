import numpy as np

from backend.python.Logger import Logger
from backend.python.enums import *

class Visualizer:

    @staticmethod
    def get_heatmap(points, h, w):
        res = 50
        yy, xx = np.meshgrid(np.linspace(-h, h, res), np.linspace(-w, w, res))
        zz = np.zeros_like(xx)
        dw, dh = (2 * w + 1) / res, (2 * h + 1) / res
        for p in points:
            if p.features[p.ID, PF_state] == State_INFECTED:
                x = p.features[p.ID, PF_px]
                y = p.features[p.ID, PF_py]
                if x > w or y > h:
                    Logger.log("Person outside map", 'c')
                    continue
                try:
                    zz[int(x // dw) + res // 2, int(y // dh) + res // 2] += 1  # todo bugsy
                except IndexError as e:
                    Logger.log(str(e), 'c')
        return xx, yy, zz

