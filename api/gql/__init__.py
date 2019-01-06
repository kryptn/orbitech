import graphene


class Query(graphene.ObjectType):
    satellite = graphene.Field('gql.Satellite',
                               name=graphene.Argument(graphene.String, required=True),
                               description="Get a satellite by name")

    all_satellites = graphene.Field(graphene.List('gql.Satellite'),
                                    description="Get all satellites")

    next_satellite_passes = graphene.Field(graphene.List('gql.Passing'),
                                           observer=graphene.Argument('gql.ObserverInput', required=True),
                                           length=graphene.Argument(graphene.Int, description="hours from now"),
                                           horizon=graphene.Argument(graphene.Float, description="observer's horizon"),
                                           description="Get next satellite passes")

    def resolve_all_satellites(self, info, **kwargs):
        tles = info.context['tles']

        return [Satellite(name=name, tle=tle) for name, tle in tles.items()]

    def resolve_next_satellite_passes(self, info, length, observer, horizon=0, **kwargs):
        satellites = Query.resolve_all_satellites(self, info, **kwargs)

        passes = []

        for sat in satellites:
            next_passes = sat.resolve_next_passes(info, length, horizon, observer, **kwargs)
            passes.extend(next_passes or [])

        return sorted(passes, key=lambda p: p.rise.time)

    def resolve_satellite(self, info, name):
        tles = info.context['tles']

        this_tle = tles.get(name.upper())

        return Satellite(name=name, tle=this_tle)


from gql.satellite import Satellite
from gql.observer import ObserverInput, Observer
from gql.passing import Passing
from gql.position import Position

schema = graphene.Schema(query=Query)
