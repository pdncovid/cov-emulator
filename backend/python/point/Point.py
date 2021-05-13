import numpy as np

from backend.python.enums import State
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport


def get_transmission_p(beta, d, infected_duration):
    # 0 - 1
    def distance_f(d):
        return np.exp(-d / 5)

    def duration_f(dt):
        return np.exp(-abs(np.random.normal(7, 2) - dt))

    dp = distance_f(d)
    tp = duration_f(infected_duration)
    return beta * dp * tp ** 0.3


class Point:
    normal_temperature = (36.8, 1.0)
    infect_temperature = (37.4, 1.2)

    def __init__(self, x, y):
        self.x = x  # x location
        self.y = y  # y location
        self.vx = 0  # velocity x
        self.vy = 0  # velocity y

        self.route = []  # route that point is going to take. (list of location refs)
        self.duration_time = []  # time spent on each location
        self.current_location = -1  # current location in the route (index of the route list)
        self.main_trans = None  # main transport medium the point will use

        self.wealth = 0  # wealth class of the point
        self.behaviour = 0  # behaviour of the point (healthy medical practices -> unhealthy)

        self.state = State.SUSCEPTIBLE.value  # current state of the point (infected/dead/recovered etc.)

        self.source = None  # infected source point
        self.infected_time = -1  # infected time
        self.infected_location = None  # infected location (ID)

        self.tested_positive_time = -1  # tested positive time

        self.temp = 0  # temperature of the point
        self.update_temp(0.0)

    def set_route(self, route, duration):
        assert len(route) == len(duration)
        self.route = route
        self.duration_time = duration
        self.current_location = 0

    def get_current_location(self) -> Location:
        return self.route[self.current_location]

    def get_next_location(self) -> Location:
        return self.route[(self.current_location + 1) % len(self.route)]

    def set_infected(self, t, p, common_p):
        self.state = State.INFECTED.value
        self.infected_time = t
        self.source = p
        self.update_temp(common_p)

    def set_recovered(self):
        self.state = State.RECOVERED.value

    def set_susceptible(self):
        self.state = State.SUSCEPTIBLE.value

    def transmit_disease(self, point, beta, common_p, d, t):
        rnd = np.random.rand()
        infected_duration = t - point.infected_time
        tr_p =get_transmission_p(beta, d, infected_duration)
        if rnd < tr_p:
            self.set_infected(t, point, common_p)
            return True
        return False

    def update_temp(self, common_p):
        if self.state == State.INFECTED.value:
            self.temp = np.random.normal(*Point.infect_temperature)
        else:
            if np.random.rand() < common_p:  # Common fever
                self.temp = np.random.normal(*Point.infect_temperature)
            else:
                self.temp = np.random.normal(*Point.normal_temperature)
