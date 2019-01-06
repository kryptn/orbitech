import graphene


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
