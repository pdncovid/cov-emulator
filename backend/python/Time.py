import datetime
import pandas as pd
import numpy as np


class Time:
    _shift_hrs = 4
    _scale = 5
    t = 0
    t_minutes = 0
    DAY = -1

    @staticmethod
    def init():
        Time.t = 0
        Time.t_minutes = Time._shift_hrs*60
        Time.DAY = Time.get_duration(24)

    @staticmethod
    def set_t(t):
        Time.t = t
        Time.t_minutes = Time._shift_hrs*60 + Time._scale*t

    @staticmethod
    def increment_time_unit():
        Time.t += 1
        Time.t_minutes += Time._scale

    @staticmethod
    def get_time():
        return Time.t

    @staticmethod
    def get_duration(hours: float):
        return hours * (60 / Time._scale)

    @staticmethod
    def get_time_from_datetime(hours, mins=0):
        return (hours - Time._shift_hrs) % 24 * (60 / Time._scale) + mins / Time._scale

    @staticmethod
    def get_random_time_between(t, h1, m1, h2, m2):
        return (t - t % Time.DAY) + np.random.randint(Time.get_time_from_datetime(h1, m1),
                                                      Time.get_time_from_datetime(h2, m2))

    @staticmethod
    def i_to_time(i):
        hrs = Time._shift_hrs + (i // (60 / Time._scale))
        days = hrs // 24
        return f"Day {int(days)} {(int(hrs) % 24):02d}:{int(i % (60 / Time._scale) * Time._scale):02d}"

    @staticmethod
    def i_to_datetime(i):
        string = Time.i_to_time(i)
        _, day, hours = string.split(" ")
        return pd.to_datetime(pd.to_datetime(hours).value + datetime.timedelta(days=int(day) - 1).total_seconds() * 1e9)

    @staticmethod
    def i_to_minutes(i):
        hrs = Time._shift_hrs + (i // (60 / Time._scale))
        day = hrs // 24
        hrs = hrs%24
        mins = i % (60 / Time._scale) * Time._scale
        return int(hrs)*60+int(mins)+int(day)*1440

        # mins = Time._shift_hrs * 60 + i*Time._scale
        # return int(mins)

        # string = Time.i_to_time(i)
        # _, day, hours = string.split(" ")
        # hrs, mins = hours.split(":")
