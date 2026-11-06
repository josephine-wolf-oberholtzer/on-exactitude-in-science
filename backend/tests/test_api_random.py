import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

LABELS = ["artist", "company", "master", "release", "track"]


@pytest.mark.asyncio
@pytest.mark.parametrize("label", [None, *LABELS])
async def test_random_redirects_to_entity(
    label: str | None,
    client: httpx.AsyncClient,
    loaded_engine: AsyncEngine,
) -> None:
    params = {"label": label} if label else {}
    expected_labels = {label} if label else set(LABELS)
    for _ in range(10):
        redirect = await client.get("/random/", params=params)
        assert redirect.status_code == 307
        assert redirect.headers["location"].startswith("/entity/")
        response = await client.get(redirect.headers["location"])
        assert response.status_code == 200
        assert response.json()["label"] in expected_labels


@pytest.mark.asyncio
@pytest.mark.parametrize("label", [None, *LABELS])
async def test_random_not_found_when_empty(
    label: str | None, client: httpx.AsyncClient, engine: AsyncEngine
) -> None:
    response = await client.get("/random/", params={"label": label} if label else {})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_random_rejects_unknown_label(client: httpx.AsyncClient) -> None:
    response = await client.get("/random/", params={"label": "nope"})
    assert response.status_code == 422
