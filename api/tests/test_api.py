import asyncio
from pathlib import Path

import pytest
import pytest_asyncio
from aiohttp.test_utils import TestClient, TestServer

from maps import app, goblin, loader


@pytest_asyncio.fixture(scope="module")
async def test_data():
    path = Path(__file__).parent
    async with goblin.GoblinManager(aliases={"g": "tg"}) as goblin_app:
        session = await goblin_app.session()
        await session.g.V().drop().toList()
        await loader.load(goblin_app, path, consumer_count=8, limit=200)
    yield


@pytest_asyncio.fixture
async def api_client(test_data):
    application = app.init_app(aliases={"g": "tg"})
    client = TestClient(TestServer(application))
    await client.start_server()
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_health(api_client):
    response = await api_client.get("/health")
    assert await response.json() == {"status": "ok"}
    assert response.status == 200


@pytest.mark.asyncio
async def test_index(api_client):
    response = await api_client.get("/")
    assert await response.json() == {"status": "ok"}
    assert response.status == 200


@pytest.mark.asyncio
async def test_random(api_client):
    results = []
    for _ in range(10):
        response = await api_client.get("/random")
        assert response.status == 200
        results.append(await response.json())
    assert len(set([result["result"]["id"] for result in results])) > 1


@pytest.mark.asyncio
async def test_random_by_label(api_client):
    for label in ["artist", "company", "master", "release", "track"]:
        results = []
        for _ in range(10):
            response = await api_client.get(f"/random/{label}")
            assert response.status == 200
            results.append(await response.json())
        assert all(result["result"]["label"] == label for result in results)
        assert len(set([result["result"]["id"] for result in results])) > 1


@pytest.mark.asyncio
async def test_search(api_client):
    await asyncio.sleep(0.5)  # Let elasticsearch catch up
    response = await api_client.get("/search?q=Mood+Swing&limit=10")
    json = await response.json()
    for entry in json["result"]:
        assert isinstance(entry["id"], int)
        assert isinstance(entry["last_modified"], str)
        assert isinstance(entry["random"], float)
        entry["id"] = ...
        entry["last_modified"] = ...
        entry["random"] = ...
    json["result"].sort(key=lambda x: (x["label"], x["eid"]))
    assert json == {
        "limit": 10,
        "query": "Mood Swing",
        "result": [
            {
                "child_count": 0,
                "eid": 8,
                "id": ...,
                "label": "artist",
                "last_modified": ...,
                "out_roles": ["Remix"],
                "name": "Mood II Swing",
                "random": ...,
                "total_edge_count": 1,
            },
            {
                "child_count": 0,
                "country": "US",
                "eid": "3-3",
                "formats": ["Compilation", "CD", "Mixed"],
                "genres": ["Electronic"],
                "id": ...,
                "in_roles": ["Includes", "Released", "Remix"],
                "label": "track",
                "last_modified": ...,
                "name": "When The Funk Hits The Fan (Mood II Swing When The Dub Hits The Fan)",
                "position": "3",
                "primacy": 2,
                "random": ...,
                "release_name": "Profound Sounds Vol. 1",
                "styles": ["Tech House", "Techno"],
                "total_edge_count": 3,
                "videos": [
                    {
                        "title": "Profound Sounds Vol. 1 - Josh Wink",
                        "url": "https://www.youtube.com/watch?v=bqUfNGJEKlo",
                    },
                    {
                        "title": "Josh Wink Profound Sounds Vol 1 Mlada "
                        "Fronta H2O Arthur Paradiso",
                        "url": "https://www.youtube.com/watch?v=UB_rOhpn5js",
                    },
                    {
                        "title": "Profound Sounds Track 1....",
                        "url": "https://www.youtube.com/watch?v=cpQWEQjunF4",
                    },
                ],
                "year": 1999,
            },
            {
                "child_count": 0,
                "country": "US",
                "eid": "60-6",
                "id": ...,
                "formats": ["Album", "CD"],
                "genres": ["Electronic"],
                "in_roles": ["Includes"],
                "label": "track",
                "last_modified": ...,
                "name": "Mood Swing",
                "position": "6",
                "primacy": 1,
                "random": ...,
                "release_name": "World Receiver",
                "styles": ["Ambient"],
                "total_edge_count": 1,
                "videos": [
                    {
                        "title": "World Receiver by Tetsu Inoue, 1996",
                        "url": "https://www.youtube.com/watch?v=grlYRK1aSus",
                    },
                    {
                        "title": "TETSU INOUE background story _ world receiver",
                        "url": "https://www.youtube.com/watch?v=0ge7OWBJoQY",
                    },
                    {
                        "title": "Tetsu Inoue - Inter Link",
                        "url": "https://www.youtube.com/watch?v=Is1nOddoQ3s",
                    },
                    {
                        "title": "Tetsu Inoue - Health Loop (World Reiceiver)",
                        "url": "https://www.youtube.com/watch?v=cA_sOjy98Lg",
                    },
                ],
                "year": 1996,
            },
        ],
    }
    assert response.status == 200


@pytest.mark.asyncio
async def test_search_by_label(api_client):
    await asyncio.sleep(0.25)  # Let elasticsearch catch up
    response = await api_client.get("/search/company?q=Seasons&limit=10")
    json = await response.json()
    for entry in json["result"]:
        assert isinstance(entry["id"], int)
        assert isinstance(entry["last_modified"], str)
        assert isinstance(entry["random"], float)
        entry["id"] = ...
        entry["last_modified"] = ...
        entry["random"] = ...
    json["result"].sort(key=lambda x: x["eid"])
    assert json == {
        "limit": 10,
        "query": "Seasons",
        "result": [
            {
                "child_count": 0,
                "eid": 3,
                "id": ...,
                "in_roles": ["Released On"],
                "label": "company",
                "last_modified": ...,
                "name": "Seasons Recordings",
                "random": ...,
                "total_edge_count": 4,
            },
        ],
    }
    assert response.status == 200


@pytest.mark.asyncio
async def test_vertex_by_goblin_id(api_client):
    response = await api_client.get("/vertex/release/1")
    json = await response.json()
    id = json["result"]["id"]
    last_modified = json["result"]["last_modified"]
    random = json["result"]["random"]
    response = await api_client.get(f"/vertex/{id}")
    assert await response.json() == {
        "result": {
            "child_count": 0,
            "country": "Sweden",
            "eid": 1,
            "formats": ["33 ⅓ RPM", '12"', "Vinyl"],
            "genres": ["Electronic"],
            "id": id,
            "in_roles": ["Released"],
            "label": "release",
            "last_modified": last_modified,
            "name": "Stockholm",
            "out_roles": ["Includes", "Released On"],
            "primacy": 1,
            "random": random,
            "styles": ["Deep House"],
            "total_edge_count": 8,
            "videos": [
                {
                    "title": "The Persuader - Östermalm",
                    "url": "https://www.youtube.com/watch?v=MpmbntGDyNE",
                },
                {
                    "title": "The Persuader - Vasastaden",
                    "url": "https://www.youtube.com/watch?v=Cawyll0pOI4",
                },
                {
                    "title": "The Persuader - Kungsholmen",
                    "url": "https://www.youtube.com/watch?v=XExCZfMCXdo",
                },
                {
                    "title": "The Persuader - Södermalm",
                    "url": "https://www.youtube.com/watch?v=WDZqiENap_U",
                },
                {
                    "title": "The Persuader - Norrmalm",
                    "url": "https://www.youtube.com/watch?v=EBBHR3EMN50",
                },
                {
                    "title": "The Persuader - Gamla Stan",
                    "url": "https://www.youtube.com/watch?v=afMHNll9EVM",
                },
            ],
            "year": 1999,
        },
    }


@pytest.mark.asyncio
async def test_vertex_by_label(api_client):
    response = await api_client.get("/vertex/release/1")
    json = await response.json()
    id = json["result"]["id"]
    last_modified = json["result"]["last_modified"]
    random = json["result"]["random"]
    assert json == {
        "result": {
            "child_count": 0,
            "country": "Sweden",
            "eid": 1,
            "formats": ["33 ⅓ RPM", '12"', "Vinyl"],
            "genres": ["Electronic"],
            "id": id,
            "in_roles": ["Released"],
            "label": "release",
            "last_modified": last_modified,
            "name": "Stockholm",
            "out_roles": ["Includes", "Released On"],
            "primacy": 1,
            "random": random,
            "styles": ["Deep House"],
            "total_edge_count": 8,
            "videos": [
                {
                    "title": "The Persuader - Östermalm",
                    "url": "https://www.youtube.com/watch?v=MpmbntGDyNE",
                },
                {
                    "title": "The Persuader - Vasastaden",
                    "url": "https://www.youtube.com/watch?v=Cawyll0pOI4",
                },
                {
                    "title": "The Persuader - Kungsholmen",
                    "url": "https://www.youtube.com/watch?v=XExCZfMCXdo",
                },
                {
                    "title": "The Persuader - Södermalm",
                    "url": "https://www.youtube.com/watch?v=WDZqiENap_U",
                },
                {
                    "title": "The Persuader - Norrmalm",
                    "url": "https://www.youtube.com/watch?v=EBBHR3EMN50",
                },
                {
                    "title": "The Persuader - Gamla Stan",
                    "url": "https://www.youtube.com/watch?v=afMHNll9EVM",
                },
            ],
            "year": 1999,
        },
    }
    assert response.status == 200


@pytest.mark.asyncio
async def test_locality_by_label(api_client):
    response = await api_client.get("/locality/release/1")
    json = await response.json()
    assert response.status == 200, json
    assert isinstance(json["result"]["center"].pop("id"), int)
    assert isinstance(json["result"]["center"].pop("last_modified"), str)
    assert isinstance(json["result"]["center"].pop("random"), float)
    assert json["result"]["center"].pop("maximum_depth") >= 8
    assert json["result"]["center"] == {
        "child_count": 0,
        "country": "Sweden",
        "depth": 0,
        "edge_count": 8,
        "eid": 1,
        "formats": ["33 ⅓ RPM", '12"', "Vinyl"],
        "genres": ["Electronic"],
        "in_roles": ["Released"],
        "label": "release",
        "name": "Stockholm",
        "out_roles": ["Includes", "Released On"],
        "pageable_edge_count": 8,
        "primacy": 1,
        "styles": ["Deep House"],
        "total_edge_count": 8,
        "videos": [
            {
                "title": "The Persuader - Östermalm",
                "url": "https://www.youtube.com/watch?v=MpmbntGDyNE",
            },
            {
                "title": "The Persuader - Vasastaden",
                "url": "https://www.youtube.com/watch?v=Cawyll0pOI4",
            },
            {
                "title": "The Persuader - Kungsholmen",
                "url": "https://www.youtube.com/watch?v=XExCZfMCXdo",
            },
            {
                "title": "The Persuader - Södermalm",
                "url": "https://www.youtube.com/watch?v=WDZqiENap_U",
            },
            {
                "title": "The Persuader - Norrmalm",
                "url": "https://www.youtube.com/watch?v=EBBHR3EMN50",
            },
            {
                "title": "The Persuader - Gamla Stan",
                "url": "https://www.youtube.com/watch?v=afMHNll9EVM",
            },
        ],
        "year": 1999,
    }
    assert 100 <= len(json["result"]["edges"]) <= 250
    assert 100 <= len(json["result"]["vertices"]) <= 250


@pytest.mark.asyncio
async def test_path(api_client):
    response = await api_client.get("/path/artist/1/release/1")
    json = await response.json()
    assert json
    assert response.status == 200
