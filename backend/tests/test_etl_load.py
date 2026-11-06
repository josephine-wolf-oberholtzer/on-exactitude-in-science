"""
Smoke tests for loading entities into Postgres.

These check overall row counts only, not specific values. Expected counts are
derived independently, by iterating the same XML archive and counting the
distinct primary keys the entities produce.
"""

import datetime
import itertools
from pathlib import Path

import pytest
from maps.etl import Artist, Company, Entity, Master, Release
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

ENTITIES = [Artist, Company, Master, Release]


async def count_rows(engine: AsyncEngine, table_name: str) -> int:
    async with engine.connect() as connection:
        result = await connection.execute(text(f'SELECT count(*) FROM "{table_name}"'))
        return result.scalar_one()


def count_expected_rows(
    entity_class: type[Entity],
    xml_path: Path,
    date: datetime.date,
    limit: int | None = None,
) -> tuple[int, int]:
    """
    Count distinct vertex and edge primary keys from the first ``limit`` entities.
    """
    vertex_keys: set[tuple] = set()
    edge_keys: set[tuple] = set()
    for entity in itertools.islice(entity_class.iterate_xml(xml_path), limit):
        for vertex in entity.to_vertex_dicts(date):
            vertex_keys.add((vertex["id"], vertex["label"], vertex["index"]))
        for edge in entity.to_edge_dicts(date):
            edge_keys.add(
                (
                    edge["this_id"],
                    edge["this_label"],
                    edge["this_index"],
                    edge["that_id"],
                    edge["that_label"],
                    edge["that_index"],
                    edge["direction"],
                    edge["name"],
                )
            )
    return len(vertex_keys), len(edge_keys)


async def run_load(
    entity_class: type[Entity],
    *,
    data_directory_path: Path,
    engine: AsyncEngine,
    limit: int | None = None,
) -> None:
    async with engine.connect() as connection:
        await entity_class.load(
            data_directory_path=data_directory_path,
            connection=connection,
            limit=limit,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("entity_class", ENTITIES, ids=lambda c: c.__name__)
async def test_load_inserts_rows(
    entity_class: type[Entity],
    engine: AsyncEngine,
    xml_directory_path: Path,
) -> None:
    xml_path, date = entity_class.get_xml_path(xml_directory_path)
    expected_vertices, expected_edges = count_expected_rows(
        entity_class, xml_path, date
    )
    assert expected_vertices > 0
    await run_load(
        entity_class,
        data_directory_path=xml_directory_path,
        engine=engine,
    )
    assert await count_rows(engine, "vertices") == expected_vertices
    assert await count_rows(engine, "edges") == expected_edges


@pytest.mark.asyncio
@pytest.mark.parametrize("entity_class", ENTITIES, ids=lambda c: c.__name__)
async def test_load_is_idempotent(
    entity_class: type[Entity],
    engine: AsyncEngine,
    xml_directory_path: Path,
) -> None:
    """
    Loading the same data twice upserts rather than duplicating rows.
    """
    await run_load(entity_class, data_directory_path=xml_directory_path, engine=engine)
    vertex_count = await count_rows(engine, "vertices")
    edge_count = await count_rows(engine, "edges")
    assert vertex_count > 0
    await run_load(entity_class, data_directory_path=xml_directory_path, engine=engine)
    assert await count_rows(engine, "vertices") == vertex_count
    assert await count_rows(engine, "edges") == edge_count


@pytest.mark.asyncio
@pytest.mark.parametrize("entity_class", ENTITIES, ids=lambda c: c.__name__)
async def test_load_respects_limit(
    entity_class: type[Entity],
    engine: AsyncEngine,
    xml_directory_path: Path,
) -> None:
    limit = 3
    xml_path, date = entity_class.get_xml_path(xml_directory_path)
    expected_vertices, expected_edges = count_expected_rows(
        entity_class, xml_path, date, limit=limit
    )
    all_vertices, _ = count_expected_rows(entity_class, xml_path, date)
    assert 0 < expected_vertices < all_vertices
    await run_load(
        entity_class,
        data_directory_path=xml_directory_path,
        engine=engine,
        limit=limit,
    )
    assert await count_rows(engine, "vertices") == expected_vertices
    assert await count_rows(engine, "edges") == expected_edges


@pytest.mark.asyncio
async def test_load_accumulates_across_entity_types(
    engine: AsyncEngine,
    xml_directory_path: Path,
) -> None:
    """
    Loading different entity types into the same tables adds rows for each.
    """
    counts = []
    for entity_class in (Artist, Master, Release):
        await run_load(
            entity_class,
            data_directory_path=xml_directory_path,
            engine=engine,
        )
        counts.append(await count_rows(engine, "vertices"))
    assert counts == sorted(set(counts))  # Strictly increasing


@pytest.mark.asyncio
async def test_load_writes_checkpoint_and_resumes(
    engine: AsyncEngine,
    xml_directory_path: Path,
    tmp_path: Path,
) -> None:
    """
    A checkpoint records the last committed entity; resuming from the first
    entity's ID skips it, and loading everything else yields the same final rows.
    """
    from maps.etl import Checkpoint

    xml_path, date = Artist.get_xml_path(xml_directory_path)
    entities = list(Artist.iterate_xml(xml_path))
    checkpoint_path = tmp_path / "checkpoint.json"
    async with engine.connect() as connection:
        await Artist.load(
            data_directory_path=xml_directory_path,
            connection=connection,
            checkpoint_path=checkpoint_path,
        )
    saved = Checkpoint.read(checkpoint_path)
    assert saved == Checkpoint("Artist", entities[-1].id, date)
    full_vertices = await count_rows(engine, "vertices")

    async with engine.connect() as connection:
        await connection.execute(text("DELETE FROM edges"))
        await connection.execute(text("DELETE FROM vertices"))
        await connection.commit()
        await Artist.load(
            data_directory_path=xml_directory_path,
            connection=connection,
            resume_after_id=entities[0].id,
        )
    expected, _ = count_expected_rows(Artist, xml_path, date)
    skipped_keys = {
        (v["id"], v["label"], v["index"]) for v in entities[0].to_vertex_dicts(date)
    }
    assert await count_rows(engine, "vertices") <= full_vertices
    assert await count_rows(engine, "vertices") >= expected - len(skipped_keys)


@pytest.mark.asyncio
async def test_resume_with_unknown_id_raises(
    engine: AsyncEngine,
    xml_directory_path: Path,
) -> None:
    async with engine.connect() as connection:
        with pytest.raises(RuntimeError, match="not found"):
            await Artist.load(
                data_directory_path=xml_directory_path,
                connection=connection,
                resume_after_id=-1,
            )
