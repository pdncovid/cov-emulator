import math
import re

import pandas as pd
import os

from backend.python.Time import Time
from backend.python.location.Location import Location
from backend.python.point.Person import Person
from backend.python.transport.Movement import Movement


def load_from_csv(log_path, date, args):
    if date != 0:
        date -= 1
    people_info = pd.read_csv(os.path.join(log_path, f'{date:05d}_person_info.csv'))
    location_info = pd.read_csv(os.path.join(log_path, f'{date:05d}_location_info.csv'))

    person_fine_info = pd.read_csv(os.path.join(log_path, f'{date:05d}.csv'))
    person_fine_info = person_fine_info.loc[person_fine_info['time'] == max(person_fine_info['time'])].set_index(
        'person')

    t = max(person_fine_info['time'])//Time._scale  # load scale as well
    t = int(math.floor(t/Time.DAY)*Time.DAY)
    Time.set_t(t)
    Person.class_df = pd.read_csv(os.path.join(log_path, f"person_classes.csv"))#.set_index('index')
    Movement.class_df = pd.read_csv(os.path.join(log_path, f"movement_classes.csv"))#.set_index('index')
    Location.class_df = pd.read_csv(os.path.join(log_path, f"location_classes.csv"))#.set_index('index')

    return location_info, people_info, person_fine_info


def find_number_of_days(log_path):
    files = [f for f in os.listdir(log_path) if re.match(r'[0-9]+\.csv', f)]
    return len(files) - 1
