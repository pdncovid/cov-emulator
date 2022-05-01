import json
import os
import sys

print("CWD", os.getcwd())
sys.path.append('../../')

import numpy as np
import pandas as pd

from backend.python.CovEngine import CovEngine
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


def get_class_info(class_name):
    return Location.class_df.loc[Location.class_df['l_class'] == class_name].iloc[0]


def initialize(args, added_containment_events, added_gathering_events, added_vaccination_events):
    from backend.python.Loader import find_number_of_days
    from backend.python.Loader import load_from_csv
    p_df = Person.class_df
    gathering_events, vaccination_events = [], []
    gather_criteria = [
        lambda x: True,
        # lambda x: x.class_name == 'Student',
        # lambda x: x.class_name == 'CommercialWorker',
        # lambda x: 14 < Person.features[x.ID, PF_age] < 45,
        # lambda x: 35 < Person.features[x.ID, PF_age] < 65,
        # lambda x: 45 < Person.features[x.ID, PF_age] < 85,
    ]

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

    if args.load_log_name != 'NONE':
        if args.load_log_day == 'None':
            log_day = find_number_of_days(args.load_log_name)
        else:
            log_day = int(args.load_log_day)
        CovEngine.on_reset_day(log_day)
        location_info, people_info = load_from_csv(
            '../../app/src/data/' + args.load_log_name, log_day, args)

    # initialize location tree
    tree_str = open(args.locationTreeData, 'r').read()
    Logger.save_tree(tree_str)
    Logger.save_args(args)

    tree = json.loads(tree_str)
    kwargs = {'name': tree['name'], 'x': 0, 'y': 0}
    if args.load_log_name != 'NONE':
        kwargs = location_info.loc[location_info['name'] == tree['name']].iloc[0]
        kwargs = kwargs.to_dict()
    root = Location(get_class_info(tree['class']), False, **kwargs)

    def dfs(tr, node):
        if tr['class'] == 'GatheringPlace':
            for ge in added_gathering_events.keys():
                ge = added_gathering_events[ge]
                if ge['name'] == tr['name']:
                    hrs, mins = ge['time'].split(":")
                    gathering_events.append(GatherEvent(
                        int(ge['day']), Time.get_time_from_datetime(int(hrs), int(mins)),
                        Time.get_duration(int(ge['duration'])), node, ge['capacity'],
                        get_random_element(gather_criteria)))  # TODO gather criteria
        if 'children' in tr.keys():
            for child in tr['children']:
                kwargs = {'name': child['name']}
                if args.load_log_name != 'NONE':
                    kwargs = location_info.loc[location_info['name'] == child['name']].iloc[0]
                    kwargs = kwargs.to_dict()
                spawn = node.spawn_sub_locations(get_class_info(child['class']), 1, spawn_sub=False, **kwargs)
                dfs(child, spawn[0])

    dfs(tree, root)

    root.add_sub_location(Cemetery(0, -80, "Cemetery", r=3))
    loc_classes = separate_into_classes(root)
    n_houses = len(loc_classes['Home'])
    Logger.log(f"Recommended 'number of people' is {n_houses * 4}", 'c')

    # initialize people
    if args.load_log_name != 'NONE':
        people = []
        for i, p in people_info.iterrows():
            _class = Person.class_df.loc[p['person_class']]
            _kwrags = p.to_dict()

            # initialize person
            if pd.isna(_class['max_passengers']):
                person = Person(_class, **_kwrags)
            else:
                person = Transporter(_class, **_kwrags)

            # assign movement
            if person.main_trans is None:
                person.set_movement(Movement.all_instances[int(_kwrags['main_trans'])])

            # assign home, home weekend, work
            person.set_home_loc(Location.all_locations[int(_kwrags['home_loc'])])
            person.set_home_w_loc(Location.all_locations[int(_kwrags['home_weekend_loc'])])
            person.set_work_loc(Location.all_locations[int(_kwrags['work_loc'])])

            # assign state parameters

            # assign latches?? NO

            # set last location (No need - they will reset anyway!)
            # Location.all_locations[person_fine_info.loc[person.ID, 'current_location_id']].enter_person(person)
            # person.set_position(person_fine_info.loc[person.ID, 'x'], person_fine_info.loc[person.ID, 'y'], force=True)
            # person.set_velocity(person_fine_info.loc[person.ID, 'vx'], person_fine_info.loc[person.ID, 'vy'])
            people.append(person)
        for person in people:
            # add infected source
            infected_t = person.features[person.ID, PF_infected_time]
            infected_source_id = int(person.features[person.ID, PF_infected_source_id])
            infected_loc_id = int(person.features[person.ID, PF_infected_loc_id])
            if infected_source_id != -1:
                person.set_infected(
                    infected_t, people[infected_source_id], Location.all_locations[infected_loc_id],
                    args.common_fever_p,
                    variant_name=person.infection_variant)
                disease_state = person.features[person.ID, PF_disease_state]
                person.set_disease_state(disease_state, person.disease_state_set_time)
    else:
        _init_people = json.loads(args.personPercentData)
        n_people = n_houses * 4
        people = []
        for key in _init_people.keys():
            _class = p_df.loc[p_df['p_class'] == _init_people[key]['p_class']].iloc[0]
            print("Initializing", _init_people[key])
            if pd.isna(_class['max_passengers']):
                to_add = [Person(_class) for _ in range(int(float(_init_people[key]['percentage']) / 100 * n_people))]
            else:
                to_add = [Transporter(_class) for _ in
                          range(int(float(_init_people[key]['percentage']) / 100 * n_people))]

            # infect people
            infect_percentage = float(_init_people[key]['ipercentage']) / 100
            if infect_percentage > 0:
                n_infect = max(1, int(len(to_add) * infect_percentage))
                Logger.log(f"Infecting {n_infect} people from {_init_people[key]['p_class']}", 'c')
                for _ in range(n_infect):
                    idx = np.random.randint(0, len(to_add))
                    to_add[idx].set_infected(0, to_add[idx], root, args.common_fever_p)
            people += to_add
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
        # for _ in range(max(1, int(args.inf_initial * n_people))):
        #     idx = np.random.randint(0, len(people))
        #     people[idx].set_infected(0, people[idx], root, args.common_fever_p)

    # setup vaccination events
    for ve in added_vaccination_events.keys():
        ve = added_vaccination_events[ve]
        vaccination_events.append((int(ve['day']), int(ve['min_age']), int(ve['max_age'])))

    # setup containment events
    containment_events = added_containment_events
    return people, root, containment_events, gathering_events, vaccination_events


def main():
    args = get_args_web_ui(os.path.basename(__file__)).parse_args()

    print(args)
    sys.setrecursionlimit(1000000)
    set_parameters(args)
    added_containment_events = json.loads(args.addedContainmentEvents)
    added_gathering_events = json.loads(args.addedGatheringEvents)
    added_vaccination_events = json.loads(args.addedVaccinationEvents)

    people, root, containment_events, gathering_events, vaccination_events = initialize(args,
                                                                                        added_containment_events,
                                                                                        added_gathering_events,
                                                                                        added_vaccination_events)

    print(f"{args.sim_days} Simulation days: {len(gathering_events)} gathering events. "
          f"{len(vaccination_events)} Vaccination.")

    executeSim(people, root, containment_events, gathering_events, vaccination_events, args)


if __name__ == "__main__":
    main()
