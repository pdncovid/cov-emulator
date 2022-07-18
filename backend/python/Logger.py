import logging
import os
import time

import pandas as pd
import numpy as np
import psutil

from backend.python.Time import Time
from backend.python.enums import *


class MyFileHandler(logging.FileHandler):
    def emit(self, record):
        if record.levelno == self.level:
            super().emit(record)


class MyStreamHandler(logging.StreamHandler):
    def __init__(self, skip_print):
        super().__init__()
        self.skip = skip_print

    def emit(self, record):
        if record.levelno != self.skip:
            super().emit(record)


class Logger:
    _logger = None
    write_level = None
    write_level_ = None
    # DAILY REPORT
    df_detailed_person = {}
    df_contacts_person = {}
    df_detailed_covid = {}
    df_detailed_resource_usage = {}
    df_resource_usage = {"day": [], "cpu_time": [], "mem": []}
    cpu_time_stamp = -1
    test_name = ''

    def __init__(self, logpath, test_name, print=True, write=False):
        if Logger._logger is None:
            Logger.test_name = test_name
            logging.getLogger('matplotlib.font_manager').disabled = True

            Logger.cpu_time_stamp = time.time()

            Logger.write_level = 'i'
            Logger.write_level_ = logging.INFO

            logging.basicConfig(
                level=logging.DEBUG,
                format='%(message)s',
                # format='%(levelname)s %(asctime)s %(message)s',
                datefmt='%m/%d/%Y%I:%M:%S %p')

            Logger._logger = logging.getLogger('my_logger')
            Logger._logger.propagate = False

            if print:
                ch = MyStreamHandler(Logger.write_level_)
                ch.setLevel(logging.ERROR)
                Logger._logger.addHandler(ch)

            if write:
                fh = MyFileHandler(logpath + test_name + '.log')
                fh.setLevel(Logger.write_level_)
                Logger._logger.addHandler(fh)

    @staticmethod
    def log(message, _type='d'):
        # if _type == 'd':
        #     Logger._logger.debug('D: ' + message)
        # if _type == 'i':
        #     Logger._logger.info('I: ' + message)
        # if _type == 'w':
        #     Logger._logger.warn('W: ' + message)
        if _type == 'e':
            Logger._logger.error('E: ' + message)
        elif _type == 'c':
            Logger._logger.critical('C: ' + message)

    @staticmethod
    def save_class_info():
        _base = f"../../app/src/data/{Logger.test_name}/"
        from backend.python.point.Person import Person
        from backend.python.transport.Movement import Movement
        from backend.python.location.Location import Location
        pd.DataFrame.to_csv(Person.class_df, _base + f"person_classes.csv", index=False)
        pd.DataFrame.to_csv(Movement.class_df, _base + f"movement_classes.csv", index=False)
        pd.DataFrame.to_csv(Location.class_df, _base + f"location_classes.csv", index=False)

    @staticmethod
    def save_log_files(t, people, locations, log_fine_details):

        from backend.python.TransmissionEngine import TransmissionEngine
        if not log_fine_details:
            Logger.df_detailed_person = pd.DataFrame({})
        _base = f"../../app/src/data/{Logger.test_name}/"
        pd.DataFrame.to_csv(Logger.df_detailed_person,  # Already converted to df
                            _base + f"{int(t // Time.DAY) - 1:05d}.csv", index=False)
        pd.DataFrame.to_csv(pd.DataFrame([p.get_description_dict() for p in people]),
                            _base + f"{int(t // Time.DAY) - 1:05d}_person_info.csv", index=False)
        pd.DataFrame.to_csv(pd.DataFrame([l.get_description_dict() for l in locations]),
                            _base + f"{int(t // Time.DAY) - 1:05d}_location_info.csv", index=False)
        pd.DataFrame.to_csv(pd.DataFrame(Logger.df_contacts_person),
                            _base + f"{int(t // Time.DAY) - 1:05d}_contact_info.csv", index=False)
        pd.DataFrame.to_csv(pd.DataFrame(Logger.df_detailed_covid),
                            _base + f"{int(t // Time.DAY) - 1:05d}_cov_info.csv", index=False)
        pd.DataFrame.to_csv(pd.DataFrame(Logger.df_detailed_resource_usage),
                            _base + f"{int(t // Time.DAY) - 1:05d}_resource_info.csv", index=False)
        phistdf = pd.DataFrame(TransmissionEngine.p_hist,
                               columns=["p", "tr_p[i]", "trans_p", "location_p", "hygiene_p", "immunity_p", "variant_p",
                                        "asym_p"])
        pd.DataFrame.to_csv(phistdf, _base + f"p_hist.csv", index=False)

        Logger.df_detailed_person = {}
        Logger.df_contacts_person = {}
        Logger.df_detailed_covid = {}
        Logger.df_detailed_resource_usage = {}

        Logger.df_resource_usage['day'].append(t // Time.DAY)
        Logger.df_resource_usage['cpu_time'].append(time.time() - Logger.cpu_time_stamp)
        Logger.df_resource_usage['mem'].append(psutil.Process(os.getpid()).memory_info().rss)
        pd.DataFrame.to_csv(pd.DataFrame(Logger.df_resource_usage), _base + f"resource_info.csv", index=False)

        Logger.cpu_time_stamp = time.time()

    @staticmethod
    def save_tree(string):
        _base = f"../../app/src/data/{Logger.test_name}/"
        with open(_base + "tree.data", 'w') as f:
            f.write(string)

    @staticmethod
    def save_args(args):
        _base = f"../../app/src/data/{Logger.test_name}/"
        args = vars(args)
        with open(_base + "args.data", 'w') as f:
            for arg in args.keys():
                f.write("--" + str(arg) + " " + str(args[arg]).replace(" ", "") + " ")

    @staticmethod
    def update_resource_usage_log():
        mins = Time.i_to_minutes(Time.get_time())
        if len(Logger.df_detailed_resource_usage.keys()) == 0:
            Logger.df_detailed_resource_usage["time"] = []
            Logger.df_detailed_resource_usage["cpu_time"] = []
            Logger.df_detailed_resource_usage["mem"] = []
        Logger.df_detailed_resource_usage["time"].append(mins)
        Logger.df_detailed_resource_usage["cpu_time"].append(time.time() - Logger.cpu_time_stamp)
        Logger.df_detailed_resource_usage["mem"].append(psutil.Process(os.getpid()).memory_info().rss)

    @staticmethod
    def update_covid_log(people, new_infected):
        from backend.python.CovEngine import CovEngine
        from backend.python.point.Person import Person
        mins = Time.i_to_minutes(Time.get_time())
        covid_stats = {s: 0 for s in States}
        covid_stats['time'] = mins
        covid_stats['NEW INFECTED'] = len(new_infected)
        if -1 in Person.features[:, PF_infected_source_id]:
            covid_stats['Re'] = pd.value_counts((Person.features[:, PF_infected_source_id])).drop(-1).mean()
        else:
            covid_stats['Re'] = pd.value_counts((Person.features[:, PF_infected_source_id])).mean()
        covid_stats['IDENTIFIED INFECTED'] = 0
        covid_stats['IN_QUARANTINE_CENTER'] = 0
        covid_stats['IN_QUARANTINE'] = 0
        covid_stats['VACCINATED_1'] = 0
        covid_stats['VACCINATED_2'] = 0
        covid_stats['ASYMPTOTIC'] = 0
        for p in people:
            covid_stats[States[int(p.features[p.ID, PF_state]) - 1]] += 1
            covid_stats['IDENTIFIED INFECTED'] += 1 if p.is_tested_positive() else 0
            covid_stats[
                'IN_QUARANTINE_CENTER'] += 1 if p.get_current_location().class_name == 'COVIDQuarantineZone' else 0
            covid_stats['IN_QUARANTINE'] += p.get_current_location().quarantined
            covid_stats['VACCINATED_1'] += 1 if p.features[p.ID, PF_immunity_boost] > 0 else 0
            covid_stats['VACCINATED_2'] += 1 if p.features[
                                                    p.ID, PF_immunity_boost] > CovEngine.immunity_boost_inc else 0
            covid_stats['ASYMPTOTIC'] += 1 if p.features[p.ID, PF_is_asymptotic] == 1 else 0
        covid_stats["TOTAL INFECTED CASES"] = covid_stats["INFECTED"] + covid_stats["DEAD"] + \
                                              covid_stats["RECOVERED"]
        if len(Logger.df_detailed_covid.keys()) == 0:
            for k in covid_stats.keys():
                Logger.df_detailed_covid[k] = []
        for k in covid_stats.keys():
            Logger.df_detailed_covid[k].append(covid_stats[k])

    @staticmethod
    def update_person_log(people):
        mins = Time.i_to_minutes(Time.get_time())
        if len(Logger.df_detailed_person.keys()) == 0:
            fine_details_p = people[0].get_fine_description_dict(mins)
            for k in fine_details_p.keys():
                Logger.df_detailed_person[k] = []
        for p in people:
            fine_details_p = p.get_fine_description_dict(mins)
            for k in fine_details_p.keys():
                Logger.df_detailed_person[k].append(fine_details_p[k])

    @staticmethod
    def update_person_contact_log(people, n_con, contacts, t):
        if len(Logger.df_contacts_person.keys()) == 0:
            Logger.df_contacts_person["person"] = []
            Logger.df_contacts_person["n_contacts"] = []
            Logger.df_contacts_person["contacts"] = []
            Logger.df_contacts_person["time"] = []
        for p in people:
            Logger.df_contacts_person["person"].append(p.ID)
            Logger.df_contacts_person["n_contacts"].append(n_con[p.ID])
            Logger.df_contacts_person["contacts"].append(
                ' '.join(map(str, contacts[p.ID])))  # directed edges from infected to sus
            Logger.df_contacts_person["time"].append(t)

    @staticmethod
    def close():
        # Shut down the logger
        logging.shutdown()
