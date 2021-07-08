
class Time:
    _shift_hrs = 4
    _scale = 1
    t = 0

    @staticmethod
    def increment_time_unit():
        Time.t += 1

    @staticmethod
    def get_time():
        return Time.t

    @staticmethod
    def get_current_time(route, time):
        # todo add the time to travel between two locations as well
        for i in range(len(route)):
            if route[i].leaving_time != -1:
                time = route[i].leaving_time
            else:
                time += route[i].duration_time
        return time


    @staticmethod
    def get_duration(hours: float):
        return int(hours * (60 // Time._scale))

    @staticmethod
    def get_time_from_dattime(hours, mins=0):
        return (hours - Time._shift_hrs) % 24 * (60 // Time._scale) + mins // Time._scale

    @staticmethod
    def i_to_time(i):
        hrs = Time._shift_hrs + (i // (60 // Time._scale))
        days = hrs // 24
        return f"Day {days} {(hrs % 24):02d}{(i % (60 // Time._scale) * Time._scale):02d}h"