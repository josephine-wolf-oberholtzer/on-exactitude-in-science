import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

LABELS = ["artist", "company", "master", "release", "track"]


@pytest.mark.asyncio
@pytest.mark.parametrize("label", LABELS)
async def test_locality(
    label: str, client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    # Find an entity that exists, by following a random redirect
    redirect = await client.get("/random/", params={"label": label})
    entity = (await client.get(redirect.headers["location"])).json()
    response = await client.get(
        "/locality/",
        params={"eid": entity["id"], "index": entity["index"], "label": label},
    )
    assert response.status_code == 200
    body = response.json()
    vertices = {vertex["id"]: vertex for vertex in body["vertices"]}
    # The center vertex is in the locality, at distance zero
    center = vertices[body["id"]]
    assert (center["eid"], center["label"], center["distance"]) == (
        entity["id"],
        label,
        0,
    )
    # Every edge connects vertices that are in the locality
    for edge in body["edges"]:
        assert edge["this_id"] in vertices
        assert edge["that_id"] in vertices
    pagination = body["pagination"]
    assert pagination["page"] == 1
    assert pagination["total"] >= 0
    assert pagination["page_count"] >= 0


@pytest.mark.asyncio
async def test_locality_not_found(
    client: httpx.AsyncClient, loaded_engine: AsyncEngine
) -> None:
    response = await client.get(
        "/locality/", params={"eid": 999999999, "label": "artist"}
    )
    assert response.status_code == 404
