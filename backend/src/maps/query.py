import random
from collections.abc import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from .constants import VertexLabel
from .models import Vertex

MINIMUM_NAME_LENGTH = 3


async def get_vertex(
    session: AsyncSession, id: int, label: VertexLabel, index: int = 0
) -> Vertex | None:
    """
    Get a vertex by its primary key, or ``None`` if there is no such vertex.
    """
    return await session.scalar(
        select(Vertex).where(
            Vertex.id == id, Vertex.label == int(label), Vertex.index == index
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
                release.id == Vertex.id,
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
