import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

ENDPOINTS = [
    ("/random/artist/", {"artist"}),
    ("/random/company/", {"company"}),
    ("/random/master/", {"master"}),
    ("/random/release/", {"release"}),
    ("/random/track/", {"track"}),
    ("/random/", {"artist", "company", "master", "release", "track"}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(("path", "labels"), ENDPOINTS, ids=[e[0] for e in ENDPOINTS])
async def test_random_redirects_to_entity(
    path: str,
    labels: set[str],
    client: httpx.AsyncClient,
    loaded_engine: AsyncEngine,
) -> None:
    for _ in range(10):
        redirect = await client.get(path)
        assert redirect.status_code == 307
        assert redirect.headers["location"].startswith("/entity/")
        response = await client.get(redirect.headers["location"])
        assert response.status_code == 200
        assert response.json()["label"] in labels


@pytest.mark.asyncio
@pytest.mark.parametrize("path", [e[0] for e in ENDPOINTS])
async def test_random_not_found_when_empty(
    path: str, client: httpx.AsyncClient, engine: AsyncEngine
) -> None:
    response = await client.get(path)
    assert response.status_code == 404
