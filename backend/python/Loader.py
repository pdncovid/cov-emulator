import math
import re

import pandas as pd
import os

from backend.python.ContainmentEngine import ContainmentEngine
from backend.python.Logger import Logger
from backend.python.Time import Time
from backend.python.enums import Containment, State, PersonFeatures
from backend.python.functions import separate_into_classes
from backend.python.location.Location import Location
from backend.python.location.Stations.BusStation import BusStation
from backend.python.location.Stations.TukTukStation import TukTukStation
from backend.python.point.Person import Person
from backend.python.point.Transporter import Transporter
from backend.python.transport.Movement import Movement
from backend.python.transport.MovementByTransporter import MovementByTransporter


def load_from_csv(log_path, date, args):
    people_info = pd.read_csv(os.path.join(log_path, f'{date:05d}_person_info.csv'))
    location_info = pd.read_csv(os.path.join(log_path, f'{date:05d}_location_info.csv'))

    person_fine_info = pd.read_csv(os.path.join(log_path, f'{date:05d}.csv'))
    person_fine_info = person_fine_info.loc[person_fine_info['time'] == max(person_fine_info['time'])].set_index(
        'person')
    t = max(person_fine_info['time'])//Time._scale  # load scale as well
    t = int(math.ceil(t/Time.DAY)*Time.DAY)
    Time.set_t(t)

    Person.class_df = pd.read_csv(os.path.join(log_path, f"person_classes.csv")).reset_index()
    Movement.class_df = pd.read_csv(os.path.join(log_path, f"movement_classes.csv")).reset_index()
    Location.class_df = pd.read_csv(os.path.join(log_path, f"location_classes.csv")).reset_index()

    # initialize movement methods
    for i, row in Movement.class_df.iterrows():
        if row['is_transport'] == 1:
            trans = MovementByTransporter(row)
        else:
            trans = Movement(row)

    # initialize location tree
    loc = None
    for i, row in location_info.iterrows():
        class_info = Location.class_df.loc[int(row['class'])]
        if class_info['l_class'] == 'BusStation':
            loc = BusStation(class_info, False, **row.to_dict())
        elif class_info['l_class'] == 'TukTukStation':
            loc = TukTukStation(class_info, False, **row.to_dict())
        else:
            loc = Location(class_info, False, **row.to_dict())
    for i, row in location_info.iterrows():
        if row['parent_id'] >= 0:
            loc = Location.all_locations[row['id']]
            par = Location.all_locations[row['parent_id']]
            par.add_sub_location(loc)
    root = loc.get_root()
    loc_classes = separate_into_classes(root)
    n_houses = len(loc_classes['Home'])
    Logger.log(f"Recommended 'number of people' is {n_houses * 4}", 'c')

    # initialize people
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

        # set last location
        Location.all_locations[person_fine_info.loc[person.ID, 'current_location_id']].enter_person(person)
        # person.set_current_location(,Time.get_time())
        # person.get_current_location().points.append(person)
        person.set_position(person_fine_info.loc[person.ID, 'x'], person_fine_info.loc[person.ID, 'y'], force=True)
        person.set_velocity(person_fine_info.loc[person.ID, 'vx'], person_fine_info.loc[person.ID, 'vy'])
        people.append(person)
    for person in people:
        # add infected source
        infected_source_id = int(person.features[person.ID, PersonFeatures.infected_source_id.value])
        infected_loc_id = int(person.features[person.ID, PersonFeatures.infected_loc_id.value])
        if infected_source_id != -1:
            person.source = people[infected_source_id]
            person.infected_location = Location.all_locations[infected_loc_id]
    if args.containment == Containment.ROSTER.value:
        ContainmentEngine.assign_roster_days(people, root, args)

    return people, root


def find_number_of_days(log_path):
    files = [f for f in os.listdir(log_path) if re.match(r'[0-9]+\.csv', f)]
    return len(files) - 1
