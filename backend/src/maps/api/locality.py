from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import Direction, VertexLabel, VertexLabelName
from ..models import VideoDict
from ..query import get_locality as query_locality
from .dependencies import get_session
from .utility import get_vertex_url

router = APIRouter(prefix="/locality", tags=["locality"])

Session = Annotated[AsyncSession, Depends(get_session)]


class LocalityVertex(BaseModel):
    child_count: int
    country: str | None = None
    # Only populated for the center vertex: its edge counts, keyed by edge name
    edge_counts: dict[str, int] | None = None
    eid: int
    formats: list[str] | None = None
    genres: list[str] | None = None
    id: int
    index: int
    label: str
    name: str
    position: str | None = None
    styles: list[str] | None = None
    url: str
    videos: list[VideoDict] | None = None
    year: int | None = None


class LocalityEdge(BaseModel):
    direction: Direction
    name: str
    that_id: int
    this_id: int


class LocalityResponse(BaseModel):
    edges: list[LocalityEdge]
    vertices: list[LocalityVertex]


def _parse_years(years: str | None) -> tuple[int | None, int | None]:
    """
    Parse a ``START:END`` range, either end of which may be empty.
    """
    if not years:
        return (None, None)
    start, _, end = years.partition(":")
    return (int(start) if start else None, int(end) if end else None)


@router.get("/")
async def get_locality(
    request: Request,
    session: Session,
    eid: int,
    label: VertexLabelName,
    countries: Annotated[set[str] | None, Query()] = None,
    formats: Annotated[set[str] | None, Query()] = None,
    genres: Annotated[set[str] | None, Query()] = None,
    index: int = 0,
    labels: Annotated[set[VertexLabelName] | None, Query()] = None,
    roles: Annotated[set[str] | None, Query()] = None,
    styles: Annotated[set[str] | None, Query()] = None,
    years: Annotated[
        str | None,
        Query(
            description=(
                "Inclusive range of years as START:END. Either end may be left "
                "empty: 1990:1999, 1990:, :1999"
            ),
            pattern=r"^\d*:\d*$",
        ),
    ] = None,
) -> LocalityResponse:
    """
    Get the neighborhood of an entity: nearby vertices and the edges among them.

    The center vertex carries its edge counts, grouped by edge name. Every
    vertex carries a count of its children.
    """
    try:
        vertices, edges, child_counts, edge_counts = await query_locality(
            center_eid=eid,
            center_index=index,
            center_label=VertexLabel[label.name],
            countries=countries,
            formats=formats,
            genres=genres,
            labels={VertexLabel[name.name] for name in labels} if labels else None,
            roles=roles,
            session=session,
            styles=styles,
            years=_parse_years(years),
        )
    except RuntimeError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No {label.value} {eid}")
    center_vertex = vertices[0]
    return LocalityResponse(
        edges=[
            LocalityEdge(
                direction=Direction(edge.direction),
                name=edge.name,
                that_id=that_id,
                this_id=this_id,
            )
            for edge, this_id, that_id in sorted(
                edges,
                key=lambda row: (row[0].name, row[1], row[2], row[0].direction),
            )
        ],
        vertices=[
            LocalityVertex(
                child_count=child_counts.get(vertex.id, 0),
                country=vertex.country,
                edge_counts=edge_counts if vertex is center_vertex else None,
                eid=vertex.eid,
                formats=vertex.formats,
                genres=vertex.genres,
                id=vertex.id,
                index=vertex.index,
                label=VertexLabel(vertex.label).name.lower(),
                name=vertex.name,
                position=vertex.position,
                styles=vertex.styles,
                url=get_vertex_url(request, vertex),
                videos=vertex.videos,
                year=vertex.year,
            )
            for vertex in sorted(vertices, key=lambda vertex: vertex.id)
        ],
    )
