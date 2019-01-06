from datetime import datetime

import graphene

from utils import parse_useful_tle, orbital_of


class Observer(graphene.ObjectType):
    lon = graphene.Field(graphene.Float, description="observer's longitude")
    lat = graphene.Field(graphene.Float, description="observer's latitude")
    alt = graphene.Field(graphene.Float, description="observer's altitude in meters")


class SatellitePass(graphene.ObjectType):
    satellite = graphene.Field('gql.Satellite')
    observer = graphene.Field(Observer)

    rise_time = graphene.DateTime()
    fall_time = graphene.DateTime()
    max_elevation_time = graphene.DateTime()

    _satellite_pass_keys = ('rise_time', 'fall_time', 'max_elevation_time')

    @staticmethod
    def from_pass_tuple(rise, fall, max_):
        return dict(zip(SatellitePass._satellite_pass_keys, [rise, fall, max_]))


class Satellite(graphene.ObjectType):
    name = graphene.String()
    tle = graphene.String()

    observer = graphene.Field(Observer)

    next_passes = graphene.List(SatellitePass, length=graphene.Argument(graphene.Int))

    def resolve_next_passes(self, info, length, **kwargs):
        orbital = orbital_of(self.name)
        if not orbital:
            return []

        passes = orbital.get_next_passes(datetime.utcnow(), length, self.observer.lon, self.observer.lat,
                                         self.observer.alt)
        if not passes:
            return []

        return [SatellitePass(satellite=self, observer=self.observer,
                              **SatellitePass.from_pass_tuple(*p)) for p in passes]


class Query(graphene.ObjectType):
    all_satellites = graphene.List(Satellite, lon=graphene.Argument(graphene.Float),
                                   lat=graphene.Argument(graphene.Float),
                                   alt=graphene.Argument(graphene.Float))
    all_satellite_passes = graphene.List(SatellitePass,
                                         lon=graphene.Argument(graphene.Float),
                                         lat=graphene.Argument(graphene.Float),
                                         alt=graphene.Argument(graphene.Float),
                                         length=graphene.Argument(graphene.Int, description="int hours in the future"))

    def resolve_all_satellites(self, info, lon, lat, alt, **kwargs):
        observer = Observer(lon=lon, lat=lat, alt=alt)
        tles = parse_useful_tle('active.txt')

        return [Satellite(name=name.strip(), tle=tle, observer=observer) for name, tle in tles.items()]

    def resolve_all_satellite_passes(self, info, lon, lat, alt, length, **kwargs):
        observer = Observer(lon=lon, lat=lat, alt=alt)
        tles = parse_useful_tle('active.txt')

        satellites = [Satellite(name=name.strip(), tle=tle, observer=observer) for name, tle in tles.items()]

        for sat in satellites:
            sat.resolve_next_passes(info, length, **kwargs)


schema = graphene.Schema(query=Query)
