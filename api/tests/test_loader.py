import asyncio
import logging
import random
from pathlib import Path

import pytest
import pytest_asyncio
from aiogremlin.process.graph_traversal import __

from maps import loader, xml


@pytest_asyncio.fixture
async def session(goblin_app):
    yield await goblin_app.session()


@pytest.mark.asyncio
@pytest.mark.parametrize("consumer_count", [1, 8])
async def test_loader_run(goblin_app, session, consumer_count, caplog):
    caplog.set_level(logging.INFO, logger="maps")
    limit = 50
    expected_vertex_counts = {
        "artist": 50,
        "company": 50,
        "master": 50,
        "release": 50,
        "track": 246,
    }
    expected_edge_counts = {
        "Alias Of": 5,
        "Arranged By": 15,
        "Co-producer": 1,
        "Copyright (c)": 5,
        "DJ Mix": 1,
        "Distributed By": 2,
        "Includes": 246,
        "Keyboards": 1,
        "Manufactured By": 2,
        "Member Of": 7,
        "Mixed By": 1,
        "Performer": 4,
        "Phonographic Copyright (p)": 5,
        "Presenter": 1,
        "Producer": 20,
        "Recorded By": 4,
        "Released On": 50,
        "Released": 34,
        "Remix": 15,
        "Strings": 1,
        "Subsidiary Of": 1,
        "Written-By": 13,
    }
    for attempt in range(2):
        await loader.load(
            goblin_app,
            Path(__file__).parent,
            consumer_count=consumer_count,
            limit=limit,
        )
        await asyncio.sleep(2)
        actual_vertex_counts = await (
            session.traversal().V().groupCount().by(__.label())
        ).next()
        actual_edge_counts = await (
            session.traversal().E().groupCount().by(__.values("name"))
        ).next()
        print(f"Attempt {attempt}")
        assert actual_vertex_counts == expected_vertex_counts
        assert actual_edge_counts == expected_edge_counts


@pytest.mark.asyncio
async def test_load_artist_vertex(session):
    entity_id = random.randint(0, 1000)
    xml_artist = xml.Artist(entity_id=entity_id, name="Foo")
    assert (
        await session.g.V().has("artist", "artist_id", entity_id).count().next()
    ) == 0

    await loader.load_artist_vertex(session, xml_artist)
    values_a = (
        await session.g.V().has("artist", "artist_id", entity_id).valueMap().next()
    )
    last_modified_a = values_a.pop("last_modified")[0]
    random_a = values_a.pop("random")[0]
    assert values_a == {"artist_id": [entity_id], "name": ["Foo"]}

    xml_artist.name = "Foo 2"

    await loader.load_artist_vertex(session, xml_artist)
    values_b = (
        await session.g.V().has("artist", "artist_id", entity_id).valueMap().next()
    )
    last_modified_b = values_b.pop("last_modified")[0]
    random_b = values_b.pop("random")[0]
    assert values_b == {"artist_id": [entity_id], "name": ["Foo 2"]}
    assert random_b != random_a
    assert last_modified_b > last_modified_a


@pytest.mark.asyncio
async def test_load_company_vertex(session):
    entity_id = random.randint(0, 1000)
    xml_company = xml.Company(entity_id=entity_id, name="Bar")
    assert (
        await session.g.V().has("company", "company_id", entity_id).count().next()
    ) == 0

    await loader.load_company_vertex(session, xml_company)
    values_a = (
        await session.g.V().has("company", "company_id", entity_id).valueMap().next()
    )
    last_modified_a = values_a.pop("last_modified")[0]
    random_a = values_a.pop("random")[0]
    assert values_a == {"company_id": [entity_id], "name": ["Bar"]}

    xml_company.name = "Bar 2"

    await loader.load_company_vertex(session, xml_company)
    values_b = (
        await session.g.V().has("company", "company_id", entity_id).valueMap().next()
    )
    last_modified_b = values_b.pop("last_modified")[0]
    random_b = values_b.pop("random")[0]
    assert values_b == {"company_id": [entity_id], "name": ["Bar 2"]}
    assert random_b != random_a
    assert last_modified_b > last_modified_a


@pytest.mark.asyncio
async def test_load_release_vertex_properties(session):
    entity_id = random.randint(0, 1000)
    xml_release = xml.Release(
        entity_id=entity_id,
        country="US",
        formats=['12"', "EP", "33\xe2\x85\x93"],
        name="Baz",
        tracks=[
            xml.Track(entity_id=f"{entity_id}-A", name="Track A", position="A"),
            xml.Track(entity_id=f"{entity_id}-B", name="Track B", position="B"),
        ],
    )
    assert (
        await session.g.V().has("release", "release_id", entity_id).count().next()
    ) == 0

    await loader.load_release_vertex_and_edges(session, xml_release, 0)
    values_a = (
        await session.g.V().has("release", "release_id", entity_id).valueMap().next()
    )
    values_aa = (
        await session.g.V().has("track", "track_id", f"{entity_id}-A").valueMap().next()
    )
    values_ab = (
        await session.g.V().has("track", "track_id", f"{entity_id}-B").valueMap().next()
    )
    last_modified_a = values_a.pop("last_modified")[0]
    random_a = values_a.pop("random")[0]
    values_aa.pop("last_modified")
    values_ab.pop("last_modified")
    values_aa.pop("random")
    values_ab.pop("random")
    assert values_a == {
        "country": ["US"],
        "formats": ['12"', "EP", "33\xe2\x85\x93"],
        "name": ["Baz"],
        "primacy": [1],
        "release_id": [entity_id],
    }
    assert values_aa == {
        "country": ["US"],
        "formats": ['12"', "EP", "33\xe2\x85\x93"],
        "name": ["Track A"],
        "position": ["A"],
        "primacy": [1],
        "track_id": [f"{entity_id}-A"],
    }
    assert values_ab == {
        "country": ["US"],
        "formats": ['12"', "EP", "33\xe2\x85\x93"],
        "name": ["Track B"],
        "position": ["B"],
        "primacy": [1],
        "track_id": [f"{entity_id}-B"],
    }

    xml_release.name = "Baz 2"
    xml_release.formats = ["EP", "33⅓", "Vinyl"]

    await loader.load_release_vertex_and_edges(session, xml_release, 0)
    values_b = (
        await session.g.V().has("release", "release_id", entity_id).valueMap().next()
    )
    values_ba = (
        await session.g.V().has("track", "track_id", f"{entity_id}-A").valueMap().next()
    )
    values_bb = (
        await session.g.V().has("track", "track_id", f"{entity_id}-B").valueMap().next()
    )
    last_modified_b = values_b.pop("last_modified")[0]
    random_b = values_b.pop("random")[0]
    values_ba.pop("last_modified")
    values_bb.pop("last_modified")
    values_ba.pop("random")
    values_bb.pop("random")
    assert values_b == {
        "country": ["US"],
        "formats": ["EP", "Vinyl", "33⅓"],
        "name": ["Baz 2"],
        "primacy": [1],
        "release_id": [entity_id],
    }
    assert random_b != random_a
    assert last_modified_b > last_modified_a
    assert values_ba == {
        "country": ["US"],
        "formats": ["EP", "Vinyl", "33⅓"],
        "name": ["Track A"],
        "position": ["A"],
        "primacy": [1],
        "track_id": [f"{entity_id}-A"],
    }
    assert values_bb == {
        "country": ["US"],
        "formats": ["EP", "Vinyl", "33⅓"],
        "name": ["Track B"],
        "position": ["B"],
        "primacy": [1],
        "track_id": [f"{entity_id}-B"],
    }
