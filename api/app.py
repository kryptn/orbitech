import asyncio

from aiohttp import web
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from gql import schema
from utils import parse_useful_tle

router = web.RouteTableDef()


@router.route('*', '/graphql', name='graphql')
async def gql(request: web.Request) -> web.Response:
    gql_view = GraphQLView(
        schema=schema,
        executor=AsyncioExecutor(loop=asyncio.get_event_loop()),
        context={'tles': parse_useful_tle('active.txt')},
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
