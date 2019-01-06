from functools import partialmethod

import graphene


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
