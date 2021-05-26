import numpy as np

from backend.python.enums import State
from backend.python.location.Location import Location
from backend.python.transport.Transport import Transport


class Person:
    normal_temperature = (36.8, 1.0)
    infect_temperature = (37.4, 1.2)
    id = 0

    def __init__(self):
        self.id = Person.id
        Person.id += 1
        self.x = 0  # x location
        self.y = 0  # y location
        self.vx = 0  # velocity x
        self.vy = 0  # velocity y
        self.gender = 0  # gender of the person

        self.route = []  # route that point is going to take. (list of location refs)
        self.duration_time = []  # time spent on each location
        self.leaving_time = []  # time which the person will not overstay on a given location
        self.current_location = -1  # current location in the route (index of the route list)

        self.current_loc = None
        self.main_trans = None  # main transport medium the point will use
        self.current_trans = None

        self.wealth = 0  # wealth class of the point
        self.behaviour = 0  # behaviour of the point (healthy medical practices -> unhealthy)

        self.state = State.SUSCEPTIBLE.value  # current state of the point (infected/dead/recovered etc.)

        self.source = None  # infected source point
        self.infected_time = -1  # infected time
        self.infected_location = None  # infected location (ID)

        self.tested_positive_time = -1  # tested positive time

        self.temp = 0  # temperature of the point
        self.update_temp(0.0)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.id)

    def set_random_route(self, root, t, common_route_classes=None):
        if common_route_classes is None:
            common_route_classes = []
        leaves = []

        def dfs(rr: Location):
            if len(rr.locations) == 0:
                leaves.append(rr)
            for child in rr.locations:
                dfs(child)

        dfs(root)

        route = [leaves[np.random.randint(0, len(leaves))] for _ in range(np.random.randint(2, 8))]
        duration = [np.random.randint(10, 50) for _ in range(len(route))]
        leaving = [-1 for _ in range(len(route))]
        self.x = route[0].x + np.random.normal(0, 10)
        self.y = route[0].y + np.random.normal(0, 10)
        route[0].enter_person(self, t)
        self.set_route(route, duration, leaving)

    def set_route(self, route, duration, leaving):
        assert len(route) == len(duration) == len(leaving)

        self.x = route[0].x + np.random.normal(0, 1)
        self.y = route[0].y + np.random.normal(0, 1)

        self.route = route
        self.duration_time = duration
        self.leaving_time = leaving
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
            self.temp = np.random.normal(*Person.infect_temperature)
        else:
            if np.random.rand() < common_p:  # Common fever
                self.temp = np.random.normal(*Person.infect_temperature)
            else:
                self.temp = np.random.normal(*Person.normal_temperature)
