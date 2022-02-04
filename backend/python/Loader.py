import pandas as pd
import os

def load_from_csv(log_path, date):
    people_info = pd.read_csv(os.path.join(log_path, f'{date:05d}_person_info.csv'))
    location_info = pd.read_csv(os.path.join(log_path, f'{date:05d}_location_info.csv'))
    people_classes = open('people.txt', 'r').readlines()
    location_classes = open('locs.txt', 'r').readlines()
    movement_classes = open('movement.txt', 'r').readlines()

