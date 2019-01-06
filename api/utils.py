from datetime import datetime
from functools import partial
from json import JSONEncoder, dumps
from uuid import UUID

from pyorbital.orbital import Orbital


def parse_useful_tle(filename, data=None):
    if not data:
        with open(filename) as fd:
            data = fd.readlines()

    tles = {}
    while data:
        name, line1, line2, *data = data
        tles[name] = {'tle': f"{name}\n{line1}\n{line2}\n"}

    return tles


def orbital_of(satname):
    try:
        return Orbital(satname, tle_file='active.txt')
    except NotImplementedError:
        return None


class ShouldBeDefaultEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat(timespec='milliseconds')
        if isinstance(o, (UUID, )):
            return str(o)
        return super().default(o)


sane_dumps = partial(dumps, cls=ShouldBeDefaultEncoder)
