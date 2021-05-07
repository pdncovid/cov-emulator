import numpy as np


class Point:
    normal_temperature = (36.8, 1.0)
    infect_temperature = (37.4, 1.2)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 0
        self.source = None

        self.vx = 0
        self.vy = 0

        self.infected_time = -1
        self.tested_positive_time = -1

        self.temp = 0
        self.update_temp(0.0)



    def set_infected(self, t, common_p):
        self.state = 1
        self.infected_time = t
        self.update_temp(common_p)

    def set_recovered(self):
        self.state = -1

    def set_susceptible(self):
        self.state = 0

    def transmit_disease(self, point, beta,common_p, t):
        rnd = np.random.rand()
        if rnd < beta:
            self.set_infected(t, common_p)
            self.source = point

    def update_temp(self, common_p):
        if self.state == 1:
            self.temp = np.random.normal(*Point.infect_temperature)
        else:
            if np.random.rand() < common_p:  # Common fever
                self.temp = np.random.normal(*Point.infect_temperature)
            else:
                self.temp = np.random.normal(*Point.normal_temperature)
