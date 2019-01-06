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
