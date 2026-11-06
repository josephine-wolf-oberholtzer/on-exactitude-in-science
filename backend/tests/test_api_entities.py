import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

LABELS = ["artist", "company", "master", "release", "track"]


@pytest.mark.asyncio
@pytest.mark.parametrize("label", LABELS)
async def test_entity(
    label: str, client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    # Find an entity that exists, by following a random redirect
    redirect = await client.get("/random/", params={"label": label})
    expected = (await client.get(redirect.headers["location"])).json()
    assert expected["label"] == label
    response = await client.get(
        "/entity/",
        params={"id": expected["id"], "index": expected["index"], "label": label},
    )
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_entity_index_defaults_to_zero(
    client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    redirect = await client.get("/random/", params={"label": "artist"})
    entity_id = (await client.get(redirect.headers["location"])).json()["id"]
    response = await client.get("/entity/", params={"id": entity_id, "label": "artist"})
    assert response.json() == {"id": entity_id, "index": 0, "label": "artist"}


@pytest.mark.asyncio
async def test_entity_track_requires_its_index(
    client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    # Tracks are numbered from 1, so the default index of 0 finds nothing
    redirect = await client.get("/random/", params={"label": "track"})
    track = (await client.get(redirect.headers["location"])).json()
    assert track["index"] >= 1
    response = await client.get(
        "/entity/", params={"id": track["id"], "label": "track"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("label", LABELS)
async def test_entity_not_found(
    label: str, client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    response = await client.get("/entity/", params={"id": 999999999, "label": label})
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [
        {"label": "artist"},
        {"id": 1},
        {"id": 1, "label": "nope"},
        {"id": "x", "label": "artist"},
        {"id": 1, "label": "artist", "index": "x"},
    ],
    ids=["missing-id", "missing-label", "unknown-label", "bad-id", "bad-index"],
)
async def test_entity_validates_parameters(
    params: dict[str, str | int], client: httpx.AsyncClient
) -> None:
    response = await client.get("/entity/", params=params)
    assert response.status_code == 422
