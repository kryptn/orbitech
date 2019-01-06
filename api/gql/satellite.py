from datetime import datetime

import graphene

from utils import orbital_of


class Satellite(graphene.ObjectType):
    name = graphene.String()
    tle = graphene.String()

    observer = graphene.Field('gql.Observer')

    next_passes = graphene.List('gql.Passing', length=graphene.Argument(graphene.Int))

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
            return Passing(satellite=self, observer=self.observer,
                           rise=Position(time=rise, satellite=self),
                           fall=Position(time=fall, satellite=self),
                           max_elevation=Position(time=max_elevation, satellite=self), )

        return [satellite_from_pass(*pass_) for pass_ in passes]


from gql.passing import Passing
from gql.position import Position
