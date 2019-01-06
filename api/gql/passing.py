import graphene


class Passing(graphene.ObjectType):
    satellite = graphene.Field('gql.Satellite')
    observer = graphene.Field('gql.Observer')

    rise = graphene.Field('gql.Position')
    fall = graphene.Field('gql.Position')
    max_elevation = graphene.Field('gql.Position')

    def deg_from_time_attr(self, info, attr, **kwargs):
        if not self.satellite and not self.satellite.orbital:
            return None

        azimuth, elevation = self.satellite.orbital.get_observer_look(getattr(self, attr), *self.observer.u)
        print(azimuth, elevation)
        return azimuth
