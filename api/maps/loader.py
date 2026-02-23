import asyncio
import dataclasses
import datetime
import json
import logging
import random
import sys
import traceback
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple

from aiogremlin.exception import GremlinServerError
from aiogremlin.process.graph_traversal import __
from gremlin_python.process.traversal import Cardinality, P, T, WithOptions

from maps import entities, goblin, xml
from maps.k8s import TQDMK8S

logger = logging.getLogger(__name__)


async def backoff(attempts, timeout=1.0, backoff_factor=1.5):
    await asyncio.sleep(timeout * pow(backoff_factor, attempts))


async def consume_edges(
    goblin_app, iterator, consumer_id=1, timestamp=0.0, progress_bar=None
):
    procedures = {
        xml.Artist: load_artist_edges,
        xml.Company: load_company_edges,
    }
    session = await goblin_app.session()
    while (iterator_output := next(iterator)) is not None:
        entity_index, xml_entity = iterator_output
        if type(xml_entity) not in procedures:
            continue
        procedure = procedures[type(xml_entity)]
        await procedure(
            xml_entity,
            session,
            timestamp=timestamp,
            consumer_id=consumer_id,
            entity_index=entity_index,
        )
        progress_bar.update(1)


async def consume_vertices(
    goblin_app, iterator, consumer_id=1, timestamp=0.0, progress_bar=None
):
    procedures = {
        xml.Artist: load_artist_vertex,
        xml.Company: load_company_vertex,
        xml.Master: load_master_vertex,
        xml.Release: load_release_vertex_and_edges,
    }
    session = await goblin_app.session()
    while (iterator_output := next(iterator)) is not None:
        entity_index, xml_entity = iterator_output
        await upsert_vertex(session, xml_entity)
        if type(xml_entity) not in procedures:
            continue
        procedure = procedures[type(xml_entity)]
        await procedure(
            session,
            xml_entity,
            timestamp=timestamp,
            consumer_id=consumer_id,
            entity_index=entity_index,
        )
        progress_bar.update(1)


async def drop():
    async with goblin.GoblinManager() as goblin_app:
        session = await goblin_app.session()
        await session.g.V().drop().toList()


async def drop_edges(session, label, entity_id, timestamp=None, both=False, names=None):
    for attempt in range(10):
        traversal = session.g.V().has(label, f"{label}_id", entity_id)
        if both:
            traversal = traversal.bothE("relationship")
        else:
            traversal = traversal.outE("relationship")
        if names:
            traversal = traversal.has("name", P.within(*names))
        traversal = traversal.has("last_modified", P.lt(timestamp))
        traversal = traversal.drop()
        try:
            return await traversal.toList()
        except GremlinServerError as e:
            logger.error(f"Backing off: {e!s}\n{traceback.format_exc()}")
            await backoff(attempt)


async def drop_properties(session, xml_entity, entity_map, **kwargs):
    desired = {}
    search = {**dataclasses.asdict(xml_entity), **kwargs}
    for key, desired_values in search.items():
        if key not in entity_map:
            continue
        if not isinstance(desired_values, (list, set)):
            continue
        if sorted(desired_values) == sorted(entity_map[key]):
            continue
        desired[key] = desired_values
    if not desired:
        return
    label = type(xml_entity).__name__.lower()
    for attempt in range(10):
        traversal = session.g.V().has(label, f"{label}_id", xml_entity.entity_id)
        for key, desired_values in sorted(desired.items()):
            traversal = traversal.sideEffect(
                __.properties(key).hasValue(P.without(*desired_values)).drop()
            )
        traversal = traversal.id()
        try:
            return await traversal.next()
        except GremlinServerError as e:
            logger.error(f"Backing off: {e!s}\n{traceback.format_exc()}")
            await backoff(attempt)


async def drop_vertices(goblin_app, timestamp):
    session = await goblin_app.session()
    for attempt in range(10):
        traversal = session.g.V().has("last_modified", P.lt(timestamp)).count()
        try:
            total = await traversal.next()
        except GremlinServerError as e:
            logger.error(f"Backing off: {e!s}\n{traceback.format_exc()}")
            await backoff(attempt)
    logger.info(f"Found {total} stale vertices to drop.")
    if not total:
        return
    with TQDMK8S(
        desc="Purging Old Vertices",
        dynamic_ncols=True,
        file=sys.stdout,
        total=None,
    ) as progress_bar:
        batch = 100
        dropped = 1
        while dropped:
            for attempt in range(10):
                traversal = (
                    session.g.V()
                    .has("last_modified", P.lt(timestamp))
                    .limit(batch)
                    .sideEffect(__.drop())
                    .count()
                )
                try:
                    dropped = await traversal.next()
                except GremlinServerError as e:
                    logger.error(f"Backing off: {e!s}\n{traceback.format_exc()}")
                    await backoff(attempt)
            progress_bar.update(1)


def find_limit(directory_path, tag):
    xml_path = xml.get_xml_path(directory_path, tag)
    cache_path = xml_path.with_suffix("").with_suffix(".json")
    if cache_path.exists():
        return json.loads(cache_path.read_text())["count"]
    count = 0
    with TQDMK8S(
        desc=f"Counting {tag} elements",
        file=sys.stdout,
        mininterval=5.0,
        total=None,
    ) as progress_bar:
        for _ in xml.iterate_xml(xml_path, tag):
            count += 1
            progress_bar.update(1)
    cache_path.write_text(json.dumps({"count": count}))
    return count


def find_limits(path, limit: Optional[int] = None):
    if limit:
        return {
            "artists": limit,
            "companies": limit,
            "masters": limit,
            "releases": limit,
        }
    logger.info("Calculating dataset lengths ...")
    return {
        "artists": find_limit(path, "artist"),
        "companies": find_limit(path, "label"),
        "masters": find_limit(path, "master"),
        "releases": find_limit(path, "release"),
    }


async def load(
    goblin_app,
    path: Path,
    consumer_count: int = 1,
    limit: Optional[int] = None,
):
    """
    Update graph from Discogs .xml.gz files.

    Upsert vertices and edges

    Delete stale vertices and edges.
    """
    logger.info("Loading data ...")
    start_date = datetime.datetime.now()
    # Calculate limits for TQDM
    limits = find_limits(path, limit=limit)
    # Load artist, company, and master vertices.
    iterator = producer(
        path, consumer_count=consumer_count, limit=limit, releases=False
    )
    with TQDMK8S(
        desc="Artist/Company/Master Vertices",
        dynamic_ncols=True,
        file=sys.stdout,
        mininterval=5.0,
        smoothing=0.01,
        total=limits["artists"] + limits["companies"] + limits["masters"],
    ) as progress_bar:
        tasks = [
            consume_vertices(
                goblin_app,
                iterator,
                consumer_id=i,
                timestamp=start_date,
                progress_bar=progress_bar,
            )
            for i in range(consumer_count)
        ]
        await asyncio.gather(*tasks)
    # Load artist and company edges (alias-of, member-of, subsidiary-of).
    iterator = producer(
        Path(path),
        consumer_count=consumer_count,
        limit=limit,
        masters=False,
        releases=False,
    )
    with TQDMK8S(
        desc="Artist/Company Edges",
        dynamic_ncols=True,
        file=sys.stdout,
        mininterval=5.0,
        smoothing=0.01,
        total=limits["artists"] + limits["companies"],
    ) as progress_bar:
        tasks = [
            consume_edges(
                goblin_app,
                iterator,
                consumer_id=i,
                timestamp=start_date,
                progress_bar=progress_bar,
            )
            for i in range(consumer_count)
        ]
        await asyncio.gather(*tasks)
    # Load release (and track) vertices, and populate edges simultaneously.
    iterator = producer(
        Path(path),
        consumer_count=consumer_count,
        limit=limit,
        artists=False,
        companies=False,
        masters=False,
    )
    with TQDMK8S(
        desc="Releases",
        dynamic_ncols=True,
        file=sys.stdout,
        mininterval=10.0,
        smoothing=0.01,
        total=limits["releases"],
    ) as progress_bar:
        tasks = [
            consume_vertices(
                goblin_app,
                iterator,
                consumer_id=i,
                timestamp=start_date,
                progress_bar=progress_bar,
            )
            for i in range(consumer_count)
        ]
        await asyncio.gather(*tasks)
    # Drop old vertices
    await asyncio.sleep(10)  # Wait for elasticsearch to catch up.
    await drop_vertices(goblin_app, timestamp=start_date)
    logger.info("Loaded data in {}".format(datetime.datetime.now() - start_date))


async def load_artist_edges(
    xml_artist, session, timestamp=None, consumer_id=0, entity_index=0
):
    logger.debug(
        f"[{consumer_id}] E Artist {entity_index} [eid: {xml_artist.entity_id}] Loading..."
    )
    cache = {}
    for xml_alias in xml_artist.aliases:
        # alias but only from low to high id
        if xml_artist.entity_id > xml_alias.entity_id:
            continue
        source_tuple = "artist", xml_artist.entity_id
        target_tuple = "artist", xml_alias.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        result = await upsert_edge(
            session,
            source=source,
            target=target,
            source_label=entities.VertexLabelEnum.ARTIST,
            target_label=entities.VertexLabelEnum.ARTIST,
            name="Alias Of",
        )
        if result:
            source, target = result
            cache[source_tuple] = source
            cache[target_tuple] = target
    for xml_member in xml_artist.members:
        source_tuple = "artist", xml_member.entity_id
        target_tuple = "artist", xml_artist.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        result = await upsert_edge(
            session,
            source=source,
            target=target,
            source_label=entities.VertexLabelEnum.ARTIST,
            target_label=entities.VertexLabelEnum.ARTIST,
            name="Member Of",
        )
        if result:
            source, target = result
            cache[source_tuple] = source
            cache[target_tuple] = target
    await drop_edges(
        session,
        "artist",
        xml_artist.entity_id,
        timestamp=timestamp,
        both=False,
        names=["Alias Of", "Member Of"],
    )


async def load_artist_vertex(
    session, xml_artist, timestamp=None, consumer_id=0, entity_index=0
):
    logger.debug(
        f"[{consumer_id}] V Artist {entity_index} [eid: {xml_artist.entity_id}] Loading..."
    )
    entity_map = await upsert_vertex(session, xml_artist)
    await drop_properties(session, xml_artist, entity_map)


async def load_company_edges(
    xml_company, session, timestamp=None, consumer_id=0, entity_index=0
):
    logger.debug(
        f"[{consumer_id}] E Company {entity_index} [eid: {xml_company.entity_id}] Loading..."
    )
    cache = {}
    for xml_subsidiary in xml_company.subsidiaries:
        source_tuple = "company", xml_subsidiary.entity_id
        target_tuple = "company", xml_company.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        result = await upsert_edge(
            session,
            source=source,
            target=target,
            source_label=entities.VertexLabelEnum.COMPANY,
            target_label=entities.VertexLabelEnum.COMPANY,
            name="Subsidiary Of",
        )
        if result:
            source, target = result
            cache[source_tuple] = source
            cache[target_tuple] = target
    await drop_edges(
        session,
        "company",
        xml_company.entity_id,
        timestamp=timestamp,
        both=False,
        names=["Subsidiary Of"],
    )


async def load_company_vertex(
    session, xml_company, timestamp=None, consumer_id=0, entity_index=0
):
    logger.debug(
        f"[{consumer_id}] V Company {entity_index} [eid: {xml_company.entity_id}] Loading..."
    )
    entity_map = await upsert_vertex(session, xml_company)
    await drop_properties(session, xml_company, entity_map)


async def load_master_vertex(
    session, xml_master, timestamp=None, consumer_id=0, entity_index=0
):
    logger.debug(
        f"[{consumer_id}] V Master {entity_index} [eid: {xml_master.entity_id}] Loading..."
    )
    entity_map = await upsert_vertex(session, xml_master)
    await drop_properties(session, xml_master, entity_map)


async def load_release_vertex_and_edges(
    session, xml_release, timestamp=None, consumer_id=0, entity_index=0
):
    logger.debug(
        f"[{consumer_id}] V Release {entity_index} [eid: {xml_release.entity_id}] Loading..."
    )
    cache = {}
    primacy = 2
    if xml_release.is_main_release:
        primacy = 1
    elif xml_release.master_id is None:
        primacy = 1
    entity_map = await upsert_vertex(session, xml_release, primacy=primacy)
    await drop_properties(session, xml_release, entity_map)
    cache["release", xml_release.entity_id] = entity_map[T.id]
    for xml_track in xml_release.tracks:
        entity_map = await upsert_vertex(
            session,
            xml_track,
            country=xml_release.country,
            formats=xml_release.formats,
            genres=xml_release.genres,
            primacy=primacy,
            styles=xml_release.styles,
            year=xml_release.year,
        )
        await drop_properties(
            session,
            xml_track,
            entity_map,
            formats=xml_release.formats,
            genres=xml_release.genres,
            styles=xml_release.styles,
        )
        cache["track", xml_track.entity_id] = entity_map[T.id]
    for xml_artist in xml_release.artists:
        source_tuple = "artist", xml_artist.entity_id
        target_tuple = "release", xml_release.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        result = await upsert_edge(
            session,
            source=source,
            target=target,
            source_label=entities.VertexLabelEnum.ARTIST,
            target_label=entities.VertexLabelEnum.RELEASE,
            primacy=primacy,
            name="Released",
        )
        if result:
            source, target = result
            cache[source_tuple] = source
            cache[target_tuple] = target
    for xml_extra_artist in xml_release.extra_artists:
        source_tuple = "artist", xml_extra_artist.entity_id
        target_tuple = "release", xml_release.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        for role in xml_extra_artist.roles:
            result = await upsert_edge(
                session,
                source=source,
                target=target,
                source_label=entities.VertexLabelEnum.ARTIST,
                target_label=entities.VertexLabelEnum.RELEASE,
                primacy=primacy,
                name=role.name,
            )
            if result:
                source, target = result
                cache[source_tuple] = source
                cache[target_tuple] = target
    for xml_company in xml_release.companies:
        source_tuple = "company", xml_company.entity_id
        target_tuple = "release", xml_release.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        for role in xml_company.roles:
            result = await upsert_edge(
                session,
                source=source,
                target=target,
                source_label=entities.VertexLabelEnum.COMPANY,
                target_label=entities.VertexLabelEnum.RELEASE,
                primacy=primacy,
                name=role.name,
            )
            if result:
                source, target = result
                cache[source_tuple] = source
                cache[target_tuple] = target
    for xml_label in xml_release.labels:
        source_tuple = "release", xml_release.entity_id
        target_tuple = "company", xml_label.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        result = await upsert_edge(
            session,
            source=source,
            target=target,
            source_label=entities.VertexLabelEnum.RELEASE,
            target_label=entities.VertexLabelEnum.COMPANY,
            primacy=primacy,
            name="Released On",
        )
        if result:
            source, target = result
            cache[source_tuple] = source
            cache[target_tuple] = target
    if xml_release.master_id:
        source_tuple = "release", xml_release.entity_id
        target_tuple = "master", xml_release.master_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        result = await upsert_edge(
            session,
            source=source,
            target=target,
            source_label=entities.VertexLabelEnum.RELEASE,
            target_label=entities.VertexLabelEnum.MASTER,
            primacy=primacy,
            name="Subrelease Of",
        )
        if result:
            source, target = result
            cache[source_tuple] = source
            cache[target_tuple] = target
    for xml_track in xml_release.tracks:
        source_tuple = "release", xml_release.entity_id
        target_tuple = "track", xml_track.entity_id
        source = cache.get(source_tuple, source_tuple)
        target = cache.get(target_tuple, target_tuple)
        result = await upsert_edge(
            session,
            source=source,
            target=target,
            source_label=entities.VertexLabelEnum.RELEASE,
            target_label=entities.VertexLabelEnum.TRACK,
            primacy=primacy,
            name="Includes",
        )
        if result:
            source, target = result
            cache[source_tuple] = source
            cache[target_tuple] = target
        for xml_artist in xml_track.artists:
            source_tuple = "artist", xml_artist.entity_id
            target_tuple = "track", xml_track.entity_id
            source = cache.get(source_tuple, source_tuple)
            target = cache.get(target_tuple, target_tuple)
            result = await upsert_edge(
                session,
                source=source,
                target=target,
                source_label=entities.VertexLabelEnum.ARTIST,
                target_label=entities.VertexLabelEnum.TRACK,
                primacy=primacy,
                name="Released",
            )
            if result:
                source, target = result
                cache[source_tuple] = source
                cache[target_tuple] = target
        for xml_extra_artist in xml_track.extra_artists:
            source_tuple = "artist", xml_extra_artist.entity_id
            target_tuple = "track", xml_track.entity_id
            source = cache.get(source_tuple, source_tuple)
            target = cache.get(target_tuple, target_tuple)
            for role in xml_extra_artist.roles:
                result = await upsert_edge(
                    session,
                    source=source,
                    target=target,
                    source_label=entities.VertexLabelEnum.ARTIST,
                    target_label=entities.VertexLabelEnum.TRACK,
                    primacy=primacy,
                    name=role.name,
                )
                if result:
                    source, target = result
                    cache[source_tuple] = source
                    cache[target_tuple] = target
        await drop_edges(
            session, "track", xml_track.entity_id, timestamp=timestamp, both=True
        )
    await drop_edges(
        session, "release", xml_release.entity_id, timestamp=timestamp, both=True
    )


def producer(
    path: Path,
    consumer_count=1,
    limit=None,
    artists=True,
    companies=True,
    masters=True,
    releases=True,
):
    iterators: List[Generator[Any, None, None]] = []
    if artists:
        iterators.append(xml.get_artist_iterator(xml.get_xml_path(path, "artist")))
    if companies:
        iterators.append(xml.get_company_iterator(xml.get_xml_path(path, "label")))
    if masters:
        iterators.append(xml.get_master_iterator(xml.get_xml_path(path, "master")))
    if releases:
        iterators.append(xml.get_release_iterator(xml.get_xml_path(path, "release")))
    for iterator in iterators:
        for i, entity in enumerate(iterator):
            if i == limit:
                break
            yield i, entity
    for _ in range(consumer_count):
        yield None


async def upsert_vertex(session, xml_entity, **kwargs):
    # TODO: Return entity map, so we can purge stale properties
    kind = type(xml_entity).__name__
    goblin_entity = getattr(entities, kind)()
    label = kind.lower()
    kwargs = {
        **{
            key: value
            for key, value in dataclasses.asdict(xml_entity).items()
            if hasattr(goblin_entity, key) and value is not None
        },
        **{key: value for key, value in kwargs.items() if value is not None},
    }
    entity_key = f"{label}_id"
    for attempt in range(10):
        traversal = (
            session.g.V()
            .has(label, entity_key, xml_entity.entity_id)
            .fold()
            .coalesce(
                __.unfold(),
                __.addV(label).property(f"{label}_id", xml_entity.entity_id),
            )
            .property("last_modified", datetime.datetime.now())
            .property("random", random.random())
        )
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (set, list)):
                for subvalue in value:
                    traversal = traversal.property(Cardinality.set_, key, subvalue)
            else:
                traversal = traversal.property(Cardinality.single, key, value)
        traversal = traversal.valueMap().with_(WithOptions.tokens)
        try:
            return await traversal.next()
        except GremlinServerError as e:
            logger.error(f"Backing off: {e!s}\n{traceback.format_exc()}")
            await backoff(attempt)
    return None


async def upsert_edge(
    session, *, name, source, target, primacy=0, source_label=0, target_label=0
) -> Optional[Tuple[int, int]]:
    for attempt in range(10):
        traversal = session.g
        if isinstance(source, int):
            traversal = traversal.V(source)
        else:
            traversal = traversal.V().has(source[0], f"{source[0]}_id", source[1])
        traversal = traversal.as_("source")
        if isinstance(target, int):
            traversal = traversal.V(target)
        else:
            traversal = traversal.V().has(target[0], f"{target[0]}_id", target[1])
        traversal = traversal.as_("target")
        traversal = (
            traversal
            # If source or target do not yield traversers, it will not make it here
            .addE("relationship")
            .from_("source")
            .to("target")
            .property("last_modified", datetime.datetime.now())
            .property("name", name)
            .property("primacy", primacy)
            .select("source", "target")
            .by(__.id())
        )
        try:
            result = await traversal.next()
            if not result:
                return None
            return result["source"], result["target"]
        except GremlinServerError as e:
            logger.error(f"Backing off: {e!s}\n{traceback.format_exc()}")
            await backoff(attempt)
    return None
