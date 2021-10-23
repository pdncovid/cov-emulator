from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.Location import Location


def all_subclasses(cls):
    s = set()

    def f(c, lvl):
        sub = c.__subclasses__()
        for subc in sub:
            s.add(subc)
            f(subc, lvl + 1)

    f(cls, 0)

    s = set(map(lambda x: x.__name__, s))
    return s


def save_array(filename, arr):
    s = "\n".join(map(str, arr))
    print(s)
    fp = open(filename, 'w')
    fp.write(s)
    fp.close()
