import httpx
import pytest
from fastapi import FastAPI
from maps.api import create_app
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


@pytest.mark.asyncio
async def test_healthz(client: httpx.AsyncClient) -> None:
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lifespan_provides_engine(app: FastAPI) -> None:
    engine: AsyncEngine = app.state.engine
    async with engine.connect() as connection:
        assert (await connection.exec_driver_sql("SELECT 1")).scalar_one() == 1


@pytest.mark.asyncio
async def test_readyz(client: httpx.AsyncClient) -> None:
    response = await client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readyz_unavailable_when_database_unreachable(
    app: FastAPI, client: httpx.AsyncClient
) -> None:
    await app.state.engine.dispose()
    app.state.engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:1/postgres"
    )
    try:
        response = await client.get("/readyz")
    finally:
        await app.state.engine.dispose()
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


@pytest.mark.asyncio
async def test_startupz(client: httpx.AsyncClient) -> None:
    response = await client.get("/startupz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_startupz_unavailable_before_lifespan() -> None:
    # No lifespan has run, so the app has not finished starting
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/startupz")
    assert response.status_code == 503
    assert response.json() == {"status": "starting"}
