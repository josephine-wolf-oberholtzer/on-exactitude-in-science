import traceback

import aiohttp.web
from aiohttp_middlewares import cors_middleware

from .cache import Cache
from .goblin import GoblinManager
from .views import routes


async def error_middleware(app, handler):
    async def middleware_handler(request):
        try:
            return await handler(request)
        except aiohttp.web.HTTPException as exception:
            return aiohttp.web.json_response(
                {"status": exception.status, "reason": exception.reason},
                status=exception.status,
            )
        except Exception:
            return aiohttp.web.json_response(
                {
                    "status": 400,
                    "reason": "Bad Request",
                    "message": traceback.format_exc(),
                },
                status=400,
            )

    return middleware_handler


def init_app(aliases=None):
    aliases = aliases or {"g": "g"}
    app = aiohttp.web.Application(
        middlewares=[
            cors_middleware(allow_all=True, origins=["http://localhost:8080"]),
            error_middleware,
        ]
    )
    app.router.add_routes(routes)
    goblin_manager = GoblinManager(aliases=aliases)
    app.on_startup.extend([goblin_manager.on_startup, Cache.on_startup])
    app.on_cleanup.extend([goblin_manager.on_cleanup, Cache.on_cleanup])
    return app


app = init_app()
