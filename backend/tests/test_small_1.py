import os
import sys

import numpy as np
import pandas as pd

from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.GatherEvent import GatherEvent
from backend.python.Logger import Logger
from backend.python.Time import Time
from backend.python.enums import *
from backend.python.functions import get_random_element, separate_into_classes
from backend.python.location.Cemetery import Cemetery
from backend.python.location.Location import Location
from backend.python.main import executeSim, set_parameters
from backend.python.sim_args import get_args_web_ui
from backend.python.point.Person import Person
from backend.python.point.Transporter import Transporter
from backend.python.transport.Movement import Movement
from backend.python.transport.MovementByTransporter import MovementByTransporter


def initialize(args):
    from backend.python.Loader import find_number_of_days
    from backend.python.Loader import load_from_csv
    p_df = Person.class_df

    if args.load_log_name != "NONE":
        if args.load_log_day == -1:
            log_day = find_number_of_days(args.load_log_root)
        else:
            log_day = args.load_log_day

        people, root = load_from_csv(args.load_log_root, log_day, args)
    else:
        # initialize movement methods
        main_trans = []
        for i, row in Movement.class_df.iterrows():
            if row['is_transport'] == 1:
                trans = MovementByTransporter(row)
            else:
                trans = Movement(row)
            # DO NOT Add walk as a main transport!!! At minimum a person uses the bus
            if row['m_class'] in ['Walk', 'Tuktuk']:
                continue
            main_trans.append(trans)

        # initialize location tree
        root_classs = 'AvgProvince' # 'DenseDistrict'
        class_info = Location.class_df.loc[Location.class_df['l_class'] == root_classs].iloc[0]
        root = Location(class_info, spawn_sub=True, x=0, y=0, name="P1")
        root.add_sub_location(Cemetery(0, -80, "Cemetery", r=3))
        loc_classes = separate_into_classes(root)
        n_houses = len(loc_classes['Home'])
        Logger.log(f"Recommended 'number of people' is {n_houses * 4}", 'c')

        # initialize people
        n_people = n_houses * 4
        people = []
        _people = Person.class_df[["p_class", "default_percentage"]].values
        for init_people in _people:
            _class = p_df.loc[p_df['p_class'] == init_people[0]].iloc[0]
            if pd.isna(_class['max_passengers']):
                people += [Person(_class) for _ in range(int(init_people[1]/100 * n_people))]
            else:
                people += [Transporter(_class) for _ in range(int(init_people[1]/100 * n_people))]

        # set movement
        for person in people:
            if person.main_trans is None:
                person.set_movement(get_random_element(main_trans))

        # set home, home weekend, work
        for person in people:
            person.set_home_loc(get_random_element(loc_classes['Home']))  # todo
            person.set_home_w_loc(person.find_closest('Home', person.home_loc.parent_location, find_from_level=2))
            w_loc = p_df.loc[Person.features[person.ID, PF_occ], 'w_loc']
            if pd.isna(w_loc):
                person.set_work_loc(person.home_loc)
            else:
                person.set_work_loc(person.find_closest(w_loc, person.home_loc, find_from_level=-1))  # todo

        # infect people
        for _ in range(max(1, int(0.01 * n_people))):
            idx = np.random.randint(0, len(people))
            people[idx].set_infected(0, people[idx], root, args.common_fever_p)

        # if args.containment_strategy == Containment.ROSTER.name:
        #     ContainmentEngine.assign_roster_days(people, root, args)
    return people, root


def main():
    args = get_args_web_ui(os.path.basename(__file__)).parse_args()

    sys.setrecursionlimit(1000000)
    set_parameters(args)

    people, root = initialize(args)

    print(f"Test Simulation: With 10 gathering events. No Vaccination. Days={args.sim_days}")
    n_events = 10
    total_vaccination_days = 0
    vaccination_start_day = 1

    # initialize gathering events
    gather_places = root.get_locations_according_function(lambda l: l.class_name == 'GatheringPlace')
    gather_criteria = [lambda x: x.class_name == 'Student',
                       lambda x: x.class_name == 'CommercialWorker',
                       lambda x: 14 < Person.features[x.ID, PF_age] < 45]
    gather_events = []
    for ge in range(n_events):
        gathering_place = get_random_element(gather_places)
        if gathering_place is None:
            continue
        day = args.sim_days // n_events * ge
        start_time = Time.get_random_time_between(0, 16, 0, 18, 0)
        duration = Time.get_duration(2)
        gather_events.append(GatherEvent(day, start_time, duration, gathering_place,
                                         np.random.randint(int(len(people) * 0.10)),
                                         get_random_element(gather_criteria)))
    # initialize vaccination events
    vaccinate_events = []
    vd = total_vaccination_days // 4
    for vday in range(total_vaccination_days):
        if vday < vd:
            vaccinate_events.append((vday + vaccination_start_day, 60, 100))
        elif vday < vd * 2:
            vaccinate_events.append((vday + vaccination_start_day, 30, 60))
        elif vday < vd * 3:
            vaccinate_events.append((vday + vaccination_start_day, 20, 30))
        else:
            vaccinate_events.append((vday + vaccination_start_day, 12, 20))

    executeSim(people, root, {'0':{'containment_strategy':'QUARANTINE','startday':0}}, gather_events, vaccinate_events, args)


if __name__ == "__main__":
    main()
