import numpy as np

from backend.python.enums import State
from backend.python.functions import get_random_element
from backend.python.location.Location import Location
from backend.python.location.Residential.Home import Home
from backend.python.transport.Transport import Transport


class Person:
    normal_temperature = (36.8, 1.0)
    infect_temperature = (37.4, 1.2)
    _id = 0

    def __init__(self):
        self.ID = Person._id
        Person._id += 1
        self.x = 0  # x location
        self.y = 0  # y location
        self.vx = 0  # velocity x
        self.vy = 0  # velocity y
        self.gender = 0  # gender of the person

        self._backup_route = None
        self._backup_duration_time = None
        self._backup_leaving_time = None

        self.is_day_finished = False

        self.route = []  # route that point is going to take. (list of location refs)
        self.duration_time = []  # time spent on each location
        self.leaving_time = []  # time which the person will not overstay on a given location
        self.current_target_idx = -1  # current location in the route (index of the route list)
        self.current_loc_enter = -1
        self.current_loc_leave = -1

        self.current_loc = None
        self.main_trans = None  # main transport medium the point will use
        self.current_trans = None
        self.in_inter_trans = False

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
        repre = f"{self.__class__.__name__}(id={self.ID},x={self.x},y={self.y},vx={self.vx},vy={self.vy},state={self.state},"
        repre += f"gender={self.gender},is_day_finished={self.is_day_finished},"
        repre += f"current_target_idx={self.current_target_idx},"
        if self.current_loc is None:
            repre += f"current_loc_id=-1,"
        else:
            repre += f"current_loc_id={self.current_loc.ID},"
        repre += f"current_loc_enter={self.current_loc_enter},current_loc_leave={self.current_loc_leave},"
        if self.main_trans is None:
            repre += f"main_trans_id=-1,"
        else:
            repre += f"main_trans_id={self.main_trans.ID},"
        if self.current_trans is None:
            repre += f"current_trans_id=-1,"
        else:
            repre += f"current_trans_id={self.current_trans.ID},"
        repre += f"in_inter_trans={self.in_inter_trans},wealth={self.wealth},behaviour={self.behaviour},"

        if self.source is None:
            repre += f"source_id=-1,"
        else:
            repre += f"source_id={self.source.ID},"
        repre += f"infected_time={self.infected_time},"
        if self.infected_location is None:
            repre += f"infected_location_id=-1,"
        else:
            repre += f"infected_location_id={self.infected_location.ID},"

        repre += f"wealth={self.wealth},behaviour={self.behaviour},temp={self.temp},"
        repre += f"tested_positive_time={self.tested_positive_time},"
        repre += f"route=("
        for r in self.route:
            repre += f"{r.ID}|"
        repre = repre[:-1] + '),'
        repre += f"duration_time("
        for r in self.duration_time:
            repre += f"{r}|"
        repre = repre[:-1] + '),'

        repre += f"leaving_time("
        for r in self.leaving_time:
            repre += f"{r}|"
        repre = repre[:-1] + '))'

        return repre

    def __str__(self):
        return str(self.ID)

    def backup_route(self):
        if self._backup_route is None:
            self._backup_route = [r for r in self.route]
            self._backup_duration_time = [r for r in self.duration_time]
            self._backup_leaving_time = [r for r in self.leaving_time]

    def restore_route(self):
        if self._backup_route is not None:
            self.route = [r for r in self._backup_route]
            self.duration_time = [r for r in self._backup_duration_time]
            self.leaving_time = [r for r in self._backup_leaving_time]
            self._backup_route = None
            self._backup_duration_time = None
            self._backup_leaving_time = None

    def increment_target_location(self):
        self.current_target_idx = (self.current_target_idx + 1) % len(self.route)
        if self.current_target_idx == 0:
            self.is_day_finished = True

    def suggested_route(self, root, t, common_route_classes, force_dt=False):
        classes = Location.separate_into_classes(root)

        route = []
        duration = []
        leaving = []
        time = t
        for zone in common_route_classes:
            if zone not in classes.keys():
                raise Exception(f"{zone} locations not available in the location tree")
            objs = classes[zone]
            selected = get_random_element(objs)

            _route, _duration, _leaving, time = selected.get_suggested_sub_route(self, time, force_dt)

            route += _route
            duration += _duration
            leaving += _leaving
        return route, duration, leaving, time

    def set_random_route(self, root, t, common_route_classes=None):
        raise NotImplementedError()

    def update_route(self, root, t, new_route_classes=None, replace=False, keephome=True):
        """
        update the route of the person from current position onwards.
        if new_route_classes are given, new route will be randomly selected suggested routes from those classes
        :param root:
        :param t:
        :param new_route_classes:
        :return:
        """
        if new_route_classes is None:
            return
        t = t % Location._day
        self.backup_route()
        if replace:
            self.route = []
            self.duration_time = []
            self.leaving_time = []
            t = 0
        else:
            self.route = self.route[:self.current_target_idx + 1]
            self.duration_time = self.duration_time[:self.current_target_idx + 1]
            self.leaving_time = self.leaving_time[:self.current_target_idx + 1]
            # if self.route[-1] != self.current_loc:
            #     self.route += [self.current_loc]
            #     self.duration_time += [1]
            #     self.leaving_time += [-1]
            #     self.current_location += 1
        if keephome:
            if len(self.route) > 0 and isinstance(self.route[0], Home):
                pass
            else:
                self.route = [self._backup_route[0]] + self.route
                self.duration_time = [self._backup_duration_time[0]] + self.duration_time
                self.leaving_time = [self._backup_leaving_time[0]] + self.leaving_time

        route, duration, leaving, time = self.suggested_route(root, t, new_route_classes, force_dt=True)

        self.route += route
        self.duration_time += duration
        self.leaving_time += leaving

        if self.current_target_idx >= len(self.route):
            self.current_target_idx = len(route) - 1
        if replace:
            self.route[0].enter_person(self, t, target_location=None)

    def set_route(self, route, duration, leaving, t):
        assert len(route) == len(duration) == len(leaving)

        self.x = route[0].x + np.random.normal(0, 1)
        self.y = route[0].y + np.random.normal(0, 1)

        self.route = route
        self.duration_time = duration
        self.leaving_time = leaving
        self.current_target_idx = 0
        self.route[0].enter_person(self, t)

    def get_current_location(self) -> Location:
        return self.current_loc

    def get_next_location(self) -> Location:
        return self.route[(self.current_target_idx + 1) % len(self.route)]

    def set_infected(self, t, p, common_p):
        self.state = State.INFECTED.value
        self.infected_time = t
        self.source = p
        self.infected_location = p.current_loc
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
    def is_infected(self):
        return self.state == State.INFECTED.value

    def is_recovered(self):
        return self.state == State.RECOVERED.value

    def is_tested_positive(self):
        return self.tested_positive_time > 0

    def update_temp(self, common_p):
        if self.state == State.INFECTED.value:
            self.temp = np.random.normal(*Person.infect_temperature)
        else:
            if np.random.rand() < common_p:  # Common fever
                self.temp = np.random.normal(*Person.infect_temperature)
            else:
                self.temp = np.random.normal(*Person.normal_temperature)
