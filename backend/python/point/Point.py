import numpy as np

from backend.python.enums import State
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport





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

    def set_random_route(self, leaves, t):
        if len(self.route) != 0:
            self.route[self.current_location].remove_point(self)

        route = [leaves[np.random.randint(0, len(leaves))] for _ in range(np.random.randint(2, 5))]
        duration = [np.random.randint(10, 200) for _ in range(len(route))]
        self.x = route[0].x + np.random.normal(0, 10)
        self.y = route[0].y + np.random.normal(0, 10)
        route[0].add_point(self, t)
        self.set_route(route, duration)

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

    # def transmit_disease(self, points, beta, common_p, d, t):
    #     c = 0
    #     infected_duration = t - self.infected_time
    #     for i in range(len(points)):
    #         tr_p = get_transmission_p(beta, d[i], infected_duration)
    #         rnd = np.random.rand()
    #         if rnd < tr_p:
    #             points[i].set_infected(t, self, common_p)
    #             c += 1
    #     return c

    def update_temp(self, common_p):
        if self.state == State.INFECTED.value:
            self.temp = np.random.normal(*Point.infect_temperature)
        else:
            if np.random.rand() < common_p:  # Common fever
                self.temp = np.random.normal(*Point.infect_temperature)
            else:
                self.temp = np.random.normal(*Point.normal_temperature)
