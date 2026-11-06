import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Vertex, VertexLabels


async def get_random_entity(
    session: AsyncSession, label: VertexLabels | None = None
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
