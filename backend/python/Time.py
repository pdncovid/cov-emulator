
class Time:
    _shift_hrs = 4
    _scale = 1

    @staticmethod
    def get_current_time(duration, leaving, time):
        # todo add the time to travel between two locations as well
        for i in range(len(duration)):
            if leaving[i] != -1:
                time = leaving[i]
            else:
                time += duration[i]
        return time


    @staticmethod
    def get_duration(hours: float):
        return int(hours * (60 // Time._scale))

    @staticmethod
    def get_time(hours, mins=0):
        return (hours - Time._shift_hrs) % 24 * (60 // Time._scale) + mins // Time._scale

    @staticmethod
    def i_to_time(i):
        hrs = Time._shift_hrs + (i // (60 // Time._scale))
        days = hrs // 24
        return f"Day {days} {(hrs % 24):02d}{(i % (60 // Time._scale) * Time._scale):02d}h"