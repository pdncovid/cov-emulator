from backend.python.location.Districts.DenseDistrict import DenseDistrict
from backend.python.location.Location import Location


def all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])


def save_class_names(filename, arr):
    arr = map(lambda x:x.__name__, arr)
    s = "\n".join(map(str, arr))
    print(s)
    fp = open(filename, 'w')
    fp.write(s)
    fp.close()

