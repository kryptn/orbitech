import graphene


class Passing(graphene.ObjectType):
    satellite = graphene.Field('gql.Satellite')
    observer = graphene.Field('gql.Observer')

    rise = graphene.Field('gql.Position')
    fall = graphene.Field('gql.Position')
    max_elevation = graphene.Field('gql.Position')
