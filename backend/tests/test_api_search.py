import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.asyncio
async def test_search(client: httpx.AsyncClient, named_engine: AsyncEngine) -> None:
    response = await client.get("/search/", params={"name": "bjork"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert [(r["label"], r["name"]) for r in results] == [
        ("artist", "Björk"),
        ("company", "Björk Records"),
    ]
    # Each result links to its entity endpoint
    assert results[0]["url"] == "/entity/?id=1&label=artist"
    # Only tracks have a release
    assert all(r["release_name"] is None for r in results)
    entity = await client.get(results[0]["url"])
    body = entity.json()
    assert (body["id"], body["index"], body["label"]) == (1, 0, "artist")


@pytest.mark.asyncio
async def test_search_track_url(
    client: httpx.AsyncClient, named_engine: AsyncEngine
) -> None:
    response = await client.get("/search/", params={"name": "venus as a boy"})
    [result] = response.json()["results"]
    assert result["label"] == "track"
    assert result["url"] == "/entity/?id=3&label=track&index=4"
    # A track also reports the release it appears on
    assert result["release_name"] == "Debut"


@pytest.mark.asyncio
async def test_search_restricts_by_label(
    client: httpx.AsyncClient, named_engine: AsyncEngine
) -> None:
    response = await client.get(
        "/search/", params={"name": "bjork", "label": "company"}
    )
    assert [r["name"] for r in response.json()["results"]] == ["Björk Records"]


@pytest.mark.asyncio
async def test_search_respects_limit(
    client: httpx.AsyncClient, named_engine: AsyncEngine
) -> None:
    response = await client.get("/search/", params={"name": "bjork", "limit": 1})
    assert len(response.json()["results"]) == 1


@pytest.mark.asyncio
async def test_search_too_short_returns_nothing(
    client: httpx.AsyncClient, named_engine: AsyncEngine
) -> None:
    response = await client.get("/search/", params={"name": "bj"})
    assert response.status_code == 200
    assert response.json() == {"results": []}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [{}, {"name": "bjork", "label": "nope"}, {"name": "bjork", "limit": 0}],
    ids=["missing-name", "unknown-label", "limit-too-small"],
)
async def test_search_validates_parameters(
    params: dict[str, str | int], client: httpx.AsyncClient
) -> None:
    response = await client.get("/search/", params=params)
    assert response.status_code == 422
