from datetime import datetime
from functools import partialmethod

import graphene

from utils import parse_useful_tle, orbital_of


class ObserverCommon:
    lon = graphene.Field(graphene.Float, description="observer's longitude", required=True)
    lat = graphene.Field(graphene.Float, description="observer's latitude", required=True)
    alt = graphene.Field(graphene.Float, description="observer's altitude in meters", required=True, default_value=0)


class Observer(ObserverCommon, graphene.ObjectType):

    @property
    def u(self):
        return (self.lon, self.lat, self.alt)


class ObserverInput(ObserverCommon, graphene.InputObjectType):
    pass


class Position(graphene.ObjectType):
    satellite = graphene.Field('gql.Satellite')

    time = graphene.DateTime()
    azimuth = graphene.Float()
    elevation = graphene.Float()

    _gol = None

    def observer_look(self, info, attr, **kwargs):
        if self._gol:
            return self._gol.get(attr)

        observer = getattr(self.satellite, 'observer')
        if not observer:
            return None

        azimuth, elevation = self.satellite.orbital.get_observer_look(self.time, *observer.u)

        self._gol = {'azimuth': azimuth, 'elevation': elevation}

        return self._gol.get(attr)

    resolve_azimuth = partialmethod(observer_look, attr='azimuth')
    resolve_elevation = partialmethod(observer_look, attr='elevation')


class SatellitePass(graphene.ObjectType):
    satellite = graphene.Field('gql.Satellite')
    observer = graphene.Field(Observer)

    rise = graphene.Field(Position)
    fall = graphene.Field(Position)
    max_elevation = graphene.Field(Position)

    def deg_from_time_attr(self, info, attr, **kwargs):
        if not self.satellite and not self.satellite.orbital:
            return None

        azimuth, elevation = self.satellite.orbital.get_observer_look(getattr(self, attr), *self.observer.u)
        print(azimuth, elevation)
        return azimuth


class Satellite(graphene.ObjectType):
    name = graphene.String()
    tle = graphene.String()

    observer = graphene.Field(Observer)

    next_passes = graphene.List(SatellitePass, length=graphene.Argument(graphene.Int))

    _orbital = None

    @property
    def orbital(self):
        if not self._orbital:
            self._orbital = orbital_of(self.name)

        return self._orbital

    def resolve_next_passes(self, info, length, **kwargs):
        if not self.orbital:
            return []

        passes = self.orbital.get_next_passes(datetime.utcnow(), length, *self.observer.u)
        if not passes:
            return []

        def satellite_from_pass(rise, fall, max_elevation):
            return SatellitePass(satellite=self, observer=self.observer,
                                 rise=Position(time=rise, satellite=self),
                                 fall=Position(time=fall, satellite=self),
                                 max_elevation=Position(time=max_elevation, satellite=self), )

        return [satellite_from_pass(*pass_) for pass_ in passes]


class Query(graphene.ObjectType):
    all_satellites = graphene.Field(graphene.List(Satellite),
                                    observer=graphene.Argument(ObserverInput))
    next_satellite_passes = graphene.Field(graphene.List(SatellitePass),
                                           observer=graphene.Argument(ObserverInput),
                                           length=graphene.Argument(graphene.Int))

    def resolve_all_satellites(self, info, observer, **kwargs):
        tles = info.context['tles']

        return [Satellite(name=name.strip(), tle=tle, observer=Observer(**observer)) for name, tle in tles.items()]

    def resolve_next_satellite_passes(self, info, length, observer, **kwargs):
        tles = info.context['tles']

        satellites = [Satellite(name=name.strip(), tle=tle, observer=Observer(**observer)) for name, tle in
                      tles.items()]

        passes = []

        for sat in satellites:
            next_passes = sat.resolve_next_passes(info, length, **kwargs)
            passes.extend(next_passes or [])

        return sorted(passes, key=lambda p: p.rise.time)


schema = graphene.Schema(query=Query)
