from functools import partial

import graphene


class Query(graphene.ObjectType):
    all_satellites = graphene.Field(graphene.List('gql.Satellite'),
                                    observer=graphene.Argument('gql.ObserverInput'))
    next_satellite_passes = graphene.Field(graphene.List('gql.Passing'),
                                           observer=graphene.Argument('gql.ObserverInput'),
                                           length=graphene.Argument(graphene.Int))

    def resolve_all_satellites(self, info, observer, **kwargs):
        tles = info.context['tles']
        newsat = partial(Satellite, observer=Observer(**observer))

        return [newsat(name=name, tle=tle) for name, tle in tles.items()]

    def resolve_next_satellite_passes(self, info, length, observer, **kwargs):
        tles = info.context['tles']

        newsat = partial(Satellite, observer=Observer(**observer))

        satellites = [newsat(name=name, tle=tle) for name, tle in tles.items()]

        passes = []

        for sat in satellites:
            next_passes = sat.resolve_next_passes(info, length, **kwargs)
            passes.extend(next_passes or [])

        return sorted(passes, key=lambda p: p.rise.time)


from gql.satellite import Satellite
from gql.observer import ObserverInput, Observer
from gql.passing import Passing
from gql.position import Position

schema = graphene.Schema(query=Query)
