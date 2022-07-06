import numpy as np
#lakshitha is editing

INT_MAX = 10000000000


def bs(arr, v):
    l, r = 0, len(arr)
    while r - l > 0:
        #rama is here
        i = (r + l) // 2 #idling
        if arr[i] < v:
            l = i + 1
        elif arr[i] > v:
            r = i
        else:
            return i

    return l


def get_idx_most_likely(arr, method=0, scale=0.1):
    if method == 0:
        arr, idx = zip(*sorted(zip(arr, np.arange(len(arr)))))
        arr = arr[::-1]
        idx = idx[::-1]
        arr = np.cumsum(arr)
        if arr[-1] < 1e-5:
            return 0
        p = min(np.random.exponential(scale), 0.99) * arr[-1]
        return idx[bs(arr, p)]  # ERROR; IndexError: tuple index out of range

    if method == 1:
        arr = np.cumsum(arr)
        if arr[-1] < 1e-5:
            return -1
        p = np.random.rand() * arr[-1]
        return bs(arr, p)


def separate_into_classes(root):
    classes = {}

    def dfs(rr):
        if rr.class_name not in classes.keys():
            classes[rr.class_name] = []
        classes[rr.class_name].append(rr)
        for child in rr.locations:
            dfs(child)

    dfs(root)

    return classes


def find_in_subtree(c, tar, skip):
    _all = []

    def dfs(r):
        if r is None:
            return
        if r == skip:
            return
        if type(tar) == type:
            if isinstance(r, tar):
                _all.append(r)
        elif type(tar) == str:
            if r.class_name == tar:
                _all.append(r)
        elif r == tar:
            _all.append(r)
        for child in r.locations:
            if child == skip:
                continue
            dfs(child)

    dfs(c)
    return _all


def get_random_element(arr):
    if len(arr) == 0:
        raise Exception("Array size 0!")
    return arr[np.random.randint(0, len(arr))]


def count_graph_n(r):
    c = 1
    for ch in r.locations:
        c += count_graph_n(ch)
    return c


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


if __name__ == "__main__":
    print(bs([13, 45, 65], 64))
    print(bs([13, 45, 65], 65))
    print(bs([13, 45, 65], 66))
    print(bs([13, 45, 65], 13))
    print(bs([13, 45, 65], 14))
