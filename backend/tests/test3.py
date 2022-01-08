import argparse
import os
import sys
import time

import numpy as np

from backend.python.main import executeSim, set_parameters, get_args

from backend.python.GatherEvent import GatherEvent
from backend.python.Logger import Logger
from backend.python.Time import Time
from backend.python.const import work_map
from backend.python.enums import Shape, Containment
from backend.python.functions import get_random_element, separate_into_classes
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Districts.SparseDistrict import SparseDistrict
from backend.python.location.GatheringPlace import GatheringPlace
from backend.python.location.Residential.Home import Home
from backend.python.point.BusDriver import BusDriver
from backend.python.point.CommercialWorker import CommercialWorker
from backend.python.point.GarmentAdmin import GarmentAdmin
from backend.python.point.GarmentWorker import GarmentWorker
from backend.python.point.Retired import Retired
from backend.python.point.Student import Student
from backend.python.point.Teacher import Teacher
from backend.python.point.TuktukDriver import TuktukDriver
from backend.python.transport.Bus import Bus
from backend.python.transport.Car import Car
from backend.python.transport.Tuktuk import Tuktuk


def initialize():
    # initialize location tree
    root = SparseDistrict(Shape.CIRCLE.value, 0, 0, "D1", r=500)
    root.add_sub_location(Cemetery(Shape.CIRCLE.value, 0, -80, "Cemetery", r=3))
    loc_classes = separate_into_classes(root)
    n_houses = len(loc_classes[Home])

    Logger.log(f"Recommended 'number of people' is {n_houses * 4}", 'c')

    # initialize people
    args.n = n_houses * 4
    people = []
    people += [CommercialWorker() for _ in range(int(0.3 * args.n))]
    people += [GarmentWorker() for _ in range(int(0.25 * args.n))]
    people += [GarmentAdmin() for _ in range(int(0.03 * args.n))]
    people += [Student() for _ in range(int(0.15 * args.n))]
    people += [Teacher() for _ in range(int(0.03 * args.n))]
    people += [Retired() for _ in range(int(0.1 * args.n))]

    people += [BusDriver() for _ in range(int(0.15 * args.n))]
    people += [TuktukDriver() for _ in range(int(0.05 * args.n))]
    # people += [CommercialZoneBusDriver() for _ in range(int(0.03 * args.n))]
    # people += [SchoolBusDriver() for _ in range(int(0.02 * args.n))]

    for _ in range(int(args.i * args.n)):
        idx = np.random.randint(0, len(people))
        people[idx].set_infected(0, people[idx], args.common_p)

    # set random routes for each person and set their main transportation method
    # walk = Walk() # DO NOT Add walk as a main transport!!! At minimum a person uses the bus
    # combus = CommercialZoneBus()
    # schoolbus = SchoolBus()

    bus = Bus()
    car = Car()
    tuktuk = Tuktuk()
    main_trans = [bus, car]

    for person in people:
        if person.main_trans is None:
            person.main_trans = get_random_element(main_trans)
        person.set_home_loc(get_random_element(loc_classes[Home]))  # todo
        person.home_weekend_loc = person.find_closest('Home', person.home_loc.parent_location, find_from_level=2)
        if work_map[person.__class__] is None:
            person.work_loc = person.home_loc
        else:
            person.work_loc = person.find_closest(work_map[person.__class__], person.home_loc,
                                                  find_from_level=-1)  # todo

    return people, root


if __name__ == "__main__":
    args = get_args(os.path.basename(__file__))

    sys.setrecursionlimit(1000000)
    set_parameters(args)

    print(f"Test Simulation: With no gathering events. With Vaccination. Days={args.days}")
    n_events = 0
    vaccination_start_day = 15
    total_vaccination_days = args.days - vaccination_start_day
    people, root = initialize()

    # initialize gathering events
    gather_places = root.get_locations_according_function(lambda l: isinstance(l, GatheringPlace))
    gather_criteria = [lambda x: isinstance(x, Student),
                       lambda x: isinstance(x, CommercialWorker),
                       lambda x: 14 < x.age < 45]
    gather_events = []
    for ge in range(n_events):
        gathering_place = get_random_element(gather_places)
        if gathering_place is None:
            continue
        day = np.random.randint(0, args.days)
        start_time = Time.get_random_time_between(0, 16, 0, 18, 0)
        duration = Time.get_duration(2)
        gather_events.append(GatherEvent(day, start_time, duration, gathering_place,
                                         np.random.randint(int(args.n * 0.10)),
                                         get_random_element(gather_criteria)))
    # initialize vaccination events
    vaccinate_events = []
    vd = total_vaccination_days//4
    for vday in range(total_vaccination_days):
        if vday < vd:
            vaccinate_events.append((vday + vaccination_start_day, 60, 100))
        elif vday < vd*2:
            vaccinate_events.append((vday + vaccination_start_day, 30, 60))
        elif vday < vd*3:
            vaccinate_events.append((vday + vaccination_start_day, 20, 30))
        else:
            vaccinate_events.append((vday + vaccination_start_day, 12, 20))

    executeSim(people, root, gather_events, vaccinate_events, args)
