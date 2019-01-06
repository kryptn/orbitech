from datetime import datetime

import graphene
import numpy
from graphql import GraphQLError

from utils import orbital_of


def element_getter(attr):
    def getter(self, info, **kwargs):
        orbital = self.orbital
        if orbital:
            obj = getattr(orbital.orbit_elements, attr)
            if isinstance(obj, numpy.datetime64):
                return obj.astype(datetime)

            return obj

        return None

    return getter


class Satellite(graphene.ObjectType):
    name = graphene.String()
    tle = graphene.String()

    observer = graphene.Field('gql.Observer')

    next_passes = graphene.List('gql.Passing',
                                length=graphene.Argument(graphene.Int, required=True),
                                horizon=graphene.Argument(graphene.Float),
                                observer=graphene.Argument('gql.ObserverInput', required=True))

    epoch = graphene.Field(graphene.DateTime, resolver=element_getter('epoch'))
    eccentricity = graphene.Field(graphene.Float, resolver=element_getter('excentricity'))  # sic
    inclination = graphene.Field(graphene.Float, resolver=element_getter('inclination'))
    right_ascension = graphene.Field(graphene.Float, resolver=element_getter('right_ascension'))
    arg_perigee = graphene.Field(graphene.Float, resolver=element_getter('arg_perigee'))
    mean_anomaly = graphene.Field(graphene.Float, resolver=element_getter('mean_anomaly'))
    mean_motion = graphene.Field(graphene.Float, resolver=element_getter('mean_motion'))
    mean_motion_derivative = graphene.Field(graphene.Float, resolver=element_getter('mean_motion_derivative'))
    mean_motion_sec_derivative = graphene.Field(graphene.Float, resolver=element_getter('mean_motion_sec_derivative'))
    bstar = graphene.Field(graphene.Float, resolver=element_getter('bstar'))
    original_mean_motion = graphene.Field(graphene.Float, resolver=element_getter('original_mean_motion'))
    semi_major_axis = graphene.Field(graphene.Float, resolver=element_getter('semi_major_axis'))
    period = graphene.Field(graphene.Float, resolver=element_getter('period'))
    perigee = graphene.Field(graphene.Float, resolver=element_getter('perigee'))
    right_ascension_lon = graphene.Field(graphene.Float, resolver=element_getter('right_ascension_lon'))

    _orbital = None

    @property
    def orbital(self):
        if not self._orbital:
            self._orbital = orbital_of(self.name)

        return self._orbital

    def resolve_next_passes(self, info, length, horizon=0, observer=None, **kwargs):
        if not self.orbital:
            return []

        if observer:
            observer = Observer(**observer)

        if not observer and not self.observer:
            raise GraphQLError("cannot calculate passes without an observer")

        self.observer = observer or self.observer

        passes = self.orbital.get_next_passes(datetime.utcnow(), length, *(observer or self.observer).u,
                                              horizon=horizon)
        if not passes:
            return []

        def satellite_from_pass(rise, fall, max_elevation):
            return Passing(satellite=self, observer=observer or self.observer,
                           rise=Position(time=rise, satellite=self),
                           fall=Position(time=fall, satellite=self),
                           max_elevation=Position(time=max_elevation, satellite=self), )

        return [satellite_from_pass(*pass_) for pass_ in passes]


from gql.passing import Passing
from gql.position import Position
from gql.observer import Observer
