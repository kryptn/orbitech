import asyncio
from datetime import datetime
from json import JSONEncoder

from aiohttp import web
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from gql import schema

router = web.RouteTableDef()


class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat(timespec='milliseconds')
        return super().default(o)


@router.route('*', '/graphql', name='graphql')
async def gql(request: web.Request) -> web.Response:
    gql_view = GraphQLView(
        schema=schema,
        executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
        context={},
        graphiql=True

    )

    return await gql_view(request)


def create_app(loop=None):
    app = web.Application(loop=loop)

    app.router.add_routes(router)

    return app


if __name__ == '__main__':
    app = create_app()

    web.run_app(app, host='0.0.0.0', port='8080')
