import enum
import random
from collections.abc import Sequence

from sqlalchemy import BinaryExpression, ColumnElement, and_, func, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from .constants import Direction, VertexLabel
from .models import Edge, Vertex

MINIMUM_NAME_LENGTH = 3


class BooleanOp(enum.StrEnum):
    AND = "and"
    OR = "or"


async def get_locality(
    *,
    session: AsyncSession,
    center_eid: int,
    center_index: int = 0,
    center_label: VertexLabel,
    countries: set[str] | None = None,
    formats: set[str] | None = None,
    formats_op: BooleanOp = BooleanOp.OR,
    genres: set[str] | None = None,
    labels: set[VertexLabel] | None = None,
    inner_limit: int = 50,
    outer_limit: int = 10,
    total_limit: int = 500,
    main_releases_only: bool = True,
    offset: int = 0,
    roles: set[str] | None = None,
    styles: set[str] | None = None,
    styles_op: BooleanOp = BooleanOp.OR,
    years: tuple[int | None, int | None] = (None, None),
) -> tuple[list[Vertex], list[tuple[Edge, int, int]], dict[int, int], dict[str, int]]:
    center_vertex = await get_vertex(
        session=session, eid=center_eid, label=center_label, index=center_index
    )
    if center_vertex is None:
        raise RuntimeError
    vertices: list[Vertex] = [center_vertex]
    initial_vertex_ids: set[int] = {center_vertex.id}
    limit = inner_limit
    while len(vertices) < total_limit:
        neighbors = await _get_locality_neighbors(
            countries=countries,
            excluded_vertex_ids={vertex.id for vertex in vertices},
            formats=formats,
            formats_op=formats_op,
            genres=genres,
            initial_vertex_ids=initial_vertex_ids,
            labels=labels,
            limit=limit,
            main_releases_only=main_releases_only,
            offset=offset,
            roles=roles,
            session=session,
            styles=styles,
            styles_op=styles_op,
            years=years,
        )
        # a vertex may neighbor several initial vertices; keep one copy of each
        new_vertices = list({that.id: that for _, that in neighbors}.values())
        vertices.extend(new_vertices)
        initial_vertex_ids = {vertex.id for vertex in new_vertices}
        limit = outer_limit
        offset = 0
    vertices = vertices[:total_limit]
    edges = await _get_locality_edges(
        roles=roles,
        session=session,
        vertex_ids={vertex.id for vertex in vertices},
    )
    child_counts = await _get_locality_child_counts(
        session=session,
        vertex_ids={vertex.id for vertex in vertices},
    )
    edge_counts = await _get_locality_edge_counts(
        session=session,
        vertex_ids={center_vertex.id},
    )
    # TODO:
    #    Total edge count of each vertex, using tbe query params (supports a "get more" interaction)
    return vertices, edges, child_counts, edge_counts.get(center_vertex.id, {})


async def _get_locality_child_counts(
    *,
    session: AsyncSession,
    vertex_ids: set[int],
) -> dict[int, int]:
    query = (
        # edge filters live in the join condition, not WHERE, so that vertices
        # without matching edges survive the outer join with a count of zero
        select(Vertex.id, func.count(Edge.name))
        .select_from(Vertex)
        .outerjoin(
            Edge,
            and_(
                Edge.this_label == Vertex.label,
                Edge.this_eid == Vertex.eid,
                Edge.this_index == Vertex.index,
                Edge.name.in_(["Member Of", "Subsidiary Of", "Subrelease Of"]),
                Edge.direction == int(Direction.THAT_TO_THIS),
            ),
        )
        .where(Vertex.id.in_(vertex_ids))
        .group_by(Vertex.id)
    )
    return {
        vertex_id: count for vertex_id, count in (await session.execute(query)).tuples()
    }


async def _get_locality_edge_counts(
    *,
    session: AsyncSession,
    vertex_ids: set[int],
) -> dict[int, dict[str, int]]:
    query = (
        select(Vertex.id, Edge.name, func.count())
        .select_from(Edge)
        .join(
            Vertex,
            and_(
                Vertex.label == Edge.this_label,
                Vertex.eid == Edge.this_eid,
                Vertex.index == Edge.this_index,
            ),
        )
        .where(Vertex.id.in_(vertex_ids))
        .group_by(Vertex.id, Edge.name)
    )
    counts: dict[int, dict[str, int]] = {}
    for vertex_id, name, count in (await session.execute(query)).tuples():
        counts.setdefault(vertex_id, {})[name] = count
    return counts


async def _get_locality_edges(
    *,
    roles: set[str] | None = None,
    session: AsyncSession,
    vertex_ids: set[int],
) -> list[tuple[Edge, int, int]]:
    """
    Get the edges among the given vertices, each as a tuple of the edge, its
    ``this_vertex`` ID and its ``that_vertex`` ID.
    """
    this_vertex = aliased(Vertex, name="this_vertex")
    that_vertex = aliased(Vertex, name="that_vertex")
    query = (
        select(Edge, this_vertex.id, that_vertex.id)
        .distinct(Edge.computed_id)
        .join(
            this_vertex,
            and_(
                this_vertex.label == Edge.this_label,
                this_vertex.eid == Edge.this_eid,
                this_vertex.index == Edge.this_index,
            ),
        )
        .join(
            that_vertex,
            and_(
                that_vertex.label == Edge.that_label,
                that_vertex.eid == Edge.that_eid,
                that_vertex.index == Edge.that_index,
            ),
        )
        .where(this_vertex.id.in_(vertex_ids))
        .where(that_vertex.id.in_(vertex_ids))
    )
    if roles:
        query = query.where(Edge.name.in_(roles))
    return list((await session.execute(query)).tuples().all())


async def _get_locality_neighbors(
    *,
    countries: set[str] | None = None,
    excluded_vertex_ids: set[int],
    formats: set[str] | None = None,
    formats_op: BooleanOp = BooleanOp.OR,
    genres: set[str] | None = None,
    initial_vertex_ids: set[int],
    labels: set[VertexLabel] | None = None,
    limit: int = 10,
    main_releases_only: bool = True,
    offset: int = 0,
    roles: set[str] | None = None,
    session: AsyncSession,
    styles: set[str] | None = None,
    styles_op: BooleanOp = BooleanOp.OR,
    years: tuple[int | None, int | None] = (None, None),
) -> Sequence[tuple[Vertex, Vertex]]:
    this_vertex = aliased(Vertex, name="this_vertex")
    other_vertex = aliased(Vertex, name="other_vertex")
    # neighbors of a single this_vertex, correlated to the enclosing query
    inner = (
        select(other_vertex)
        .distinct()
        .select_from(Edge)
        .join(
            other_vertex,
            and_(
                other_vertex.label == Edge.that_label,
                other_vertex.eid == Edge.that_eid,
                other_vertex.index == Edge.that_index,
            ),
        )
        .where(
            Edge.this_label == this_vertex.label,
            Edge.this_eid == this_vertex.eid,
            Edge.this_index == this_vertex.index,
        )
        .where(other_vertex.id.not_in(excluded_vertex_ids))
        .correlate(this_vertex)
        .order_by(other_vertex.id)
        .limit(limit)
        .offset(offset)
    )
    # release & track filtering predicates
    predicates: list[ColumnElement[bool] | BinaryExpression[bool]] = []
    if countries:
        predicates.append(other_vertex.country.in_(countries))
    if formats:
        predicates.append(
            other_vertex.formats.overlap(formats)
            if formats_op == BooleanOp.OR
            else other_vertex.formats.contains(formats)
        )
    if genres:
        predicates.append(other_vertex.genres.overlap(genres))
    if styles:
        predicates.append(
            other_vertex.styles.overlap(styles)
            if styles_op == BooleanOp.OR
            else other_vertex.styles.contains(styles)
        )
    if years[0] is not None:
        predicates.append(
            or_(other_vertex.year.is_(None), other_vertex.year >= years[0])
        )
    if years[1] is not None:
        predicates.append(
            or_(other_vertex.year.is_(None), other_vertex.year <= years[1])
        )
    if labels:
        inner = inner.where(other_vertex.label.in_(labels))
    if roles:
        inner = inner.where(Edge.name.in_(roles))
    if predicates:
        inner = inner.where(
            or_(
                other_vertex.label.in_(
                    [VertexLabel.ARTIST, VertexLabel.COMPANY, VertexLabel.MASTER]
                ),
                and_(*predicates),
            )
        )
    neighbors = inner.lateral("neighbors")
    that_vertex = aliased(Vertex, neighbors, name="that_vertex")
    query = (
        select(this_vertex, that_vertex)
        .select_from(this_vertex)
        .join(neighbors, true())
        .where(this_vertex.id.in_(initial_vertex_ids))
        .order_by(this_vertex.id, that_vertex.id)
    )
    return (await session.execute(query)).tuples().all()


async def get_vertex(
    session: AsyncSession, eid: int, label: VertexLabel, index: int = 0
) -> Vertex | None:
    """
    Get a vertex by its entity ID, label and index, or ``None`` if there is none.
    """
    return await session.scalar(
        select(Vertex).where(
            Vertex.eid == eid, Vertex.label == int(label), Vertex.index == index
        )
    )


async def get_vertices_by_name(
    session: AsyncSession, name: str, label: VertexLabel | None = None, limit: int = 10
) -> Sequence[tuple[Vertex, Vertex | None]]:
    """
    Search vertices by trigram similarity to a name, most similar first.

    Each result is a vertex paired with its parent release if the vertex is a
    track, or ``None`` otherwise. A track shares its release's ID.

    Case and diacritics are ignored. Fewer than three characters is too little to
    form a useful trigram, so no results are returned.
    """
    if len(name := name.strip()) < MINIMUM_NAME_LENGTH:
        return []
    # Matches the expression of the ``ix_vertices_name_trigram`` index
    vertex_name = func.immutable_unaccent(Vertex.name)
    search_name = func.immutable_unaccent(name)
    release = aliased(Vertex)
    query = (
        select(Vertex, release)
        .outerjoin(
            release,
            and_(
                Vertex.label == int(VertexLabel.TRACK),
                release.eid == Vertex.eid,
                release.label == int(VertexLabel.RELEASE),
                release.index == 0,
            ),
        )
        # ``%`` is true above ``pg_trgm.similarity_threshold`` and uses the index
        .where(vertex_name.op("%")(search_name))
        .order_by(func.similarity(vertex_name, search_name).desc(), Vertex.name)
        .limit(limit)
    )
    if label is not None:
        query = query.where(Vertex.label == int(label))
    return (await session.execute(query)).tuples().all()


async def get_random_vertex(
    session: AsyncSession, label: VertexLabel | None = None
) -> Vertex | None:
    """
    Get a random vertex, optionally with the given label, or ``None`` if there are
    none.

    Every vertex is stamped with a uniform random float at load time. Pick a
    point on that line and take the first vertex at or after it, wrapping around
    to the start of the line if there is none.
    """
    query = select(Vertex).order_by(Vertex.random).limit(1)
    if label is not None:
        query = query.where(Vertex.label == int(label))
    for position in (random.random(), 0.0):
        if (
            vertex := await session.scalar(query.where(Vertex.random >= position))
        ) is not None:
            return vertex
    return None
