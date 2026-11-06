import re

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.asyncio
@pytest.mark.parametrize("label", ["artist", "company", "master", "release"])
async def test_entity(
    label: str, client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    redirect = await client.get("/random/", params={"label": label})
    response = await client.get(redirect.headers["location"])
    entity_id = response.json()["id"]
    response = await client.get(f"/entity/{label}/{entity_id}")
    assert response.status_code == 200
    assert response.json() == {"id": entity_id, "index": 0, "label": label}


@pytest.mark.asyncio
async def test_entity_track(
    client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    redirect = await client.get("/random/", params={"label": "track"})
    location = redirect.headers["location"]
    assert re.fullmatch(r"/entity/release/\d+/track/\d+", location)
    response = await client.get(location)
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "track"
    assert body["index"] >= 1
    assert location == f"/entity/release/{body['id']}/track/{body['index']}"


@pytest.mark.asyncio
@pytest.mark.parametrize("label", ["artist", "company", "master", "release"])
async def test_entity_not_found(
    label: str, client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    response = await client.get(f"/entity/{label}/999999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_entity_track_not_found(
    client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    response = await client.get("/entity/release/999999999/track/1")
    assert response.status_code == 404
