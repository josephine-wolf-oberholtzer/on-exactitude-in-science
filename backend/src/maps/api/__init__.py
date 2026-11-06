from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine

from .. import config
from . import entities, health, random, search


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.engine = create_async_engine(config.DATABASE_URL)
    try:
        yield
    finally:
        await app.state.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, title="On Exactitude in Science")
    app.include_router(entities.router)
    app.include_router(health.router)
    app.include_router(random.router)
    app.include_router(search.router)
    return app


__all__ = ["create_app"]
