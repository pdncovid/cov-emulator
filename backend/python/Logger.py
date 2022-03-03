import logging
import os
import time

import pandas as pd
import psutil

from backend.python.Time import Time
from backend.python.enums import State, PersonFeatures


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
    df_detailed_person = pd.DataFrame(columns=[])
    df_contacts_person = pd.DataFrame(columns=[])
    df_detailed_covid = pd.DataFrame(columns=[])
    df_detailed_resource_usage = pd.DataFrame(columns=[])
    df_resource_usage = pd.DataFrame(columns=[])
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
        if _type == 'd':
            Logger._logger.debug('D: ' + message)
        elif _type == 'i':
            Logger._logger.info('I: ' + message)
        elif _type == 'w':
            Logger._logger.warn('W: ' + message)
        elif _type == 'e':
            Logger._logger.error('E: ' + message)
        elif _type == 'c':
            Logger._logger.critical('C: ' + message)

    @staticmethod
    def log_location(loc):
        Logger.log(loc.__repr__(), Logger.write_level)

    @staticmethod
    def log_person(p):
        Logger.log(p.__repr__(), Logger.write_level)

    @staticmethod
    def log_graph(root):
        def f(r):
            Logger.log_location(r)
            for ch in r.locations:
                f(ch)

        f(root)

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
    def save_log_files(t, people, locations):
        _base = f"../../app/src/data/{Logger.test_name}/"
        pd.DataFrame.to_csv(pd.DataFrame([p.get_description_dict() for p in people]),
                            _base + f"{int(t // Time.DAY) - 1:05d}_person_info.csv", index=False)
        pd.DataFrame.to_csv(pd.DataFrame([l.get_description_dict() for l in locations]),
                            _base + f"{int(t // Time.DAY) - 1:05d}_location_info.csv", index=False)
        pd.DataFrame.to_csv(Logger.df_contacts_person,
                            _base + f"{int(t // Time.DAY) - 1:05d}_contact_info.csv", index=False)
        pd.DataFrame.to_csv(Logger.df_detailed_person,
                            _base + f"{int(t // Time.DAY) - 1:05d}.csv", index=False)
        pd.DataFrame.to_csv(Logger.df_detailed_covid,
                            _base + f"{int(t // Time.DAY) - 1:05d}_cov_info.csv", index=False)
        pd.DataFrame.to_csv(Logger.df_detailed_resource_usage,
                            _base + f"{int(t // Time.DAY) - 1:05d}_resource_info.csv", index=False)
        Logger.df_detailed_person = pd.DataFrame(columns=[])
        Logger.df_contacts_person = pd.DataFrame(columns=[])
        Logger.df_detailed_covid = pd.DataFrame(columns=[])
        Logger.df_detailed_resource_usage = pd.DataFrame(columns=[])

        Logger.df_resource_usage = Logger.df_resource_usage.append(pd.DataFrame([{'day': t // Time.DAY,
                                                                                  'cpu_time': (
                                                                                              time.time() - Logger.cpu_time_stamp),
                                                                                  'mem': psutil.Process(
                                                                                      os.getpid()).memory_info().rss}]))

        pd.DataFrame.to_csv(Logger.df_resource_usage, _base + f"resource_info.csv", index=False)

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
        Logger.df_detailed_resource_usage = Logger.df_detailed_resource_usage.append(pd.DataFrame([{
            'time': mins,
            'cpu_time': time.time() - Logger.cpu_time_stamp,
            'mem': psutil.Process(os.getpid()).memory_info().rss
        }]))

    @staticmethod
    def update_covid_log(people, new_infected):
        from backend.python.CovEngine import CovEngine
        mins = Time.i_to_minutes(Time.get_time())
        covid_stats = {State(i.value).name: 0 for i in State}
        covid_stats['time'] = mins
        covid_stats['IDENTIFIED INFECTED'] = 0
        covid_stats['IN_QUARANTINE_CENTER'] = 0
        covid_stats['IN_QUARANTINE'] = 0
        covid_stats['VACCINATED_1'] = 0
        covid_stats['VACCINATED_2'] = 0
        covid_stats['NEW INFECTED'] = len(new_infected)
        for p in people:
            covid_stats[State(p.features[p.ID, PersonFeatures.state.value]).name] += 1
            covid_stats['IDENTIFIED INFECTED'] += 1 if p.is_tested_positive() else 0
            covid_stats['IN_QUARANTINE_CENTER'] += 1 if p.get_current_location().class_name=='COVIDQuarantineZone' else 0
            covid_stats['IN_QUARANTINE'] += p.get_current_location().quarantined
            covid_stats['VACCINATED_1'] += 1 if p.features[p.ID, PersonFeatures.immunity_boost.value] > 0 else 0
            covid_stats['VACCINATED_2'] += 1 if p.features[
                                                    p.ID, PersonFeatures.immunity_boost.value] > CovEngine.immunity_boost_inc else 0
        covid_stats["TOTAL INFECTED CASES"] = covid_stats[State.INFECTED.name] + covid_stats[State.DEAD.name] + \
                                   covid_stats[State.RECOVERED.name]
        Logger.df_detailed_covid = Logger.df_detailed_covid.append(pd.DataFrame([covid_stats]))

    @staticmethod
    def update_person_log(people):
        mins = Time.i_to_minutes(Time.get_time())
        person_details_list = []
        for p in people:
            fine_details_p = p.get_fine_description_dict(mins)
            person_details_list.append(fine_details_p)
        Logger.df_detailed_person = Logger.df_detailed_person.append(pd.DataFrame(person_details_list))

    @staticmethod
    def update_person_contact_log(people, n_con, contacts, t):
        contact_details_list = []
        for p in people:
            contact_details = {'person': p.ID}
            contact_details['n_contacts'] = n_con[p.ID]
            contact_details['contacts'] = ' '.join(map(str, contacts[p.ID]))  # directed edges from infected to sus
            contact_details['time'] = t
            contact_details_list.append(contact_details)
        Logger.df_contacts_person = Logger.df_contacts_person.append(pd.DataFrame(contact_details_list))

    @staticmethod
    def close():
        # Shut down the logger
        logging.shutdown()
