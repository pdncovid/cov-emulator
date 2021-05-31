from numba import njit
import numpy as np

INT_MAX = 10000000000


@njit
def bs(arr, v):
    l, r = 0, len(arr)
    while r - l > 0:
        i = (r + l) // 2
        if arr[i] < v:
            l = i + 1
        elif arr[i] > v:
            r = i
        else:
            return i

    return l


def get_random_element(arr):
    return arr[np.random.randint(0, len(arr))]


def get_current_time(duration, leaving, time):
    for i in range(len(duration)):
        if leaving[i] != -1:
            time = leaving[i]
        else:
            time += duration[i]
    return time


def get_duration(hours: float):
    return int(hours * 60)


_shift_hrs = 4



def get_time(hours, mins=0):
    return (hours - _shift_hrs) % 24 * 60 + mins


def i_to_time(i):
    hrs = _shift_hrs + (i // 60)
    days = hrs//24
    return f"Day {days} {(hrs%24):02d}{(i % 60):02d}h"


# Given three colinear points p, q, r, the function checks if point q lies on line segment 'pr'
def onSegment(p: tuple, q: tuple, r: tuple) -> bool:
    if ((q[0] <= max(p[0], r[0])) &
            (q[0] >= min(p[0], r[0])) &
            (q[1] <= max(p[1], r[1])) &
            (q[1] >= min(p[1], r[1]))):
        return True
    return False


# To find orientation of ordered triplet (p, q, r).
# The function returns following values
# 0 --> p, q and r are colinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def orientation(p: tuple, q: tuple, r: tuple) -> int:
    val = (((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1])))

    if val == 0:
        return 0
    if val > 0:
        return 1
    else:
        return 2


def doIntersect(p1, q1, p2, q2):
    # Find the four orientations needed for
    # general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2) and (o3 != o4):
        return True

    # Special Cases
    # p1, q1 and p2 are colinear and p2 lies on segment p1q1
    if (o1 == 0) and (onSegment(p1, p2, q1)):
        return True

    # p1, q1 and p2 are colinear and q2 lies on segment p1q1
    if (o2 == 0) and (onSegment(p1, q2, q1)):
        return True

    # p2, q2 and p1 are colinear and p1 lies on segment p2q2
    if (o3 == 0) and (onSegment(p2, p1, q2)):
        return True

    # p2, q2 and q1 are colinear and q1 lies on segment p2q2
    if (o4 == 0) and (onSegment(p2, q1, q2)):
        return True

    return False


# Returns true if the point p lies  inside the polygon[] with n vertices
def is_inside_polygon(points: list, p: tuple) -> bool:
    n = len(points)

    # There must be at least 3 vertices in polygon
    if n < 3:
        return False

    # Create a point for line segment from p to infinite
    extreme = (INT_MAX, p[1])
    count = i = 0

    while True:
        next = (i + 1) % n

        # Check if the line segment from 'p' to 'extreme' intersects with the line
        # segment from 'polygon[i]' to 'polygon[next]'
        if doIntersect(points[i], points[next], p, extreme):

            # If the point 'p' is colinear with line
            # segment 'i-next', then check if it lies
            # on segment. If it lies, return true, otherwise false
            if orientation(points[i], p, points[next]) == 0:
                return onSegment(points[i], p, points[next])

            count += 1

        i = next

        if i == 0:
            break

    # Return true if count is odd, false otherwise
    return count % 2 == 1
