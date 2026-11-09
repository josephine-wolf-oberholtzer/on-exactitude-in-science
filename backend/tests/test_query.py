import datetime

import pytest
from maps.constants import VertexLabel
from maps.models import Vertex
from maps.query import get_vertices_by_name
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


async def insert_vertices(
    engine: AsyncEngine, *rows: tuple[int, VertexLabel, str]
) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            insert(Vertex),
            [
                {
                    "eid": id_,
                    "label": int(label),
                    "index": 0,
                    "name": name,
                    "random": 0.5,
                    "dataset": datetime.date(2026, 1, 1),
                }
                for id_, label, name in rows
            ],
        )


@pytest.mark.asyncio
async def test_get_vertices_by_name_ignores_diacritics_and_case(
    engine: AsyncEngine,
) -> None:
    await insert_vertices(
        engine,
        (1, VertexLabel.ARTIST, "Björk"),
        (2, VertexLabel.ARTIST, "Sigur Rós"),
    )
    async with AsyncSession(engine) as session:
        assert [v.eid for v, _ in await get_vertices_by_name(session, "bjork")] == [1]
        assert [v.eid for v, _ in await get_vertices_by_name(session, "SIGUR ROS")] == [
            2
        ]
        assert [v.eid for v, _ in await get_vertices_by_name(session, "Sigur Rós")] == [
            2
        ]


@pytest.mark.asyncio
async def test_get_vertices_by_name_orders_by_similarity(engine: AsyncEngine) -> None:
    await insert_vertices(
        engine,
        (1, VertexLabel.ARTIST, "Aphex Twin Remixes"),
        (2, VertexLabel.ARTIST, "Aphex Twin"),
        (3, VertexLabel.ARTIST, "Aphex Twins"),
    )
    async with AsyncSession(engine) as session:
        results = await get_vertices_by_name(session, "Aphex Twin")
    assert [v.eid for v, _ in results] == [2, 3, 1]


@pytest.mark.asyncio
async def test_get_vertices_by_name_restricts_by_label(engine: AsyncEngine) -> None:
    await insert_vertices(
        engine,
        (1, VertexLabel.ARTIST, "Warp Records"),
        (2, VertexLabel.COMPANY, "Warp Records"),
    )
    async with AsyncSession(engine) as session:
        both = await get_vertices_by_name(session, "Warp Records")
        companies = await get_vertices_by_name(
            session, "Warp Records", label=VertexLabel.COMPANY
        )
    assert {v.eid for v, _ in both} == {1, 2}
    assert [v.eid for v, _ in companies] == [2]


@pytest.mark.asyncio
async def test_get_vertices_by_name_respects_limit(engine: AsyncEngine) -> None:
    await insert_vertices(
        engine, *[(i, VertexLabel.ARTIST, f"Autechre {i}") for i in range(5)]
    )
    async with AsyncSession(engine) as session:
        assert len(await get_vertices_by_name(session, "Autechre", limit=3)) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["", "  ", "ab", " ab ", "Bj"])
async def test_get_vertices_by_name_requires_three_characters(
    name: str, engine: AsyncEngine
) -> None:
    await insert_vertices(engine, (1, VertexLabel.ARTIST, "Bjork"))
    async with AsyncSession(engine) as session:
        assert await get_vertices_by_name(session, name) == []


@pytest.mark.asyncio
async def test_get_vertices_by_name_joins_a_track_to_its_release(
    engine: AsyncEngine,
) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            insert(Vertex),
            [
                {
                    "eid": 7,
                    "label": int(label),
                    "index": index,
                    "name": name,
                    "random": 0.5,
                    "dataset": datetime.date(2026, 1, 1),
                }
                for label, index, name in [
                    (VertexLabel.RELEASE, 0, "Selected Ambient Works"),
                    (VertexLabel.TRACK, 1, "Xtal"),
                    # Same ID as a release, but not that release's track
                    (VertexLabel.ARTIST, 0, "Xtal Artist"),
                ]
            ],
        )
    async with AsyncSession(engine) as session:
        results = await get_vertices_by_name(session, "Xtal")
    by_label = {VertexLabel(v.label): release for v, release in results}
    assert (release := by_label[VertexLabel.TRACK]) is not None
    assert release.name == "Selected Ambient Works"
    assert by_label[VertexLabel.ARTIST] is None
