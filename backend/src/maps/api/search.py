from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import VertexLabel, VertexLabelName
from ..query import get_vertices_by_name
from .dependencies import get_session
from .utility import get_vertex_url

router = APIRouter(prefix="/search", tags=["search"])

Session = Annotated[AsyncSession, Depends(get_session)]


class SearchResult(BaseModel):
    id: int
    index: int
    label: str
    name: str
    release_name: str | None = None
    url: str


class SearchResponse(BaseModel):
    results: list[SearchResult]


@router.get("/")
async def get_entities_by_name(
    request: Request,
    session: Session,
    name: Annotated[str, Query(description="Name to search for")],
    label: VertexLabelName | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> SearchResponse:
    """
    Search entities by name, most similar first.

    Fewer than three characters returns no results.
    """
    vertices = await get_vertices_by_name(
        session,
        name,
        label=VertexLabel[label.name] if label else None,
        limit=limit,
    )
    return SearchResponse(
        results=[
            SearchResult(
                id=vertex.id,
                index=vertex.index,
                label=VertexLabel(vertex.label).name.lower(),
                name=vertex.name,
                release_name=release.name if release is not None else None,
                url=get_vertex_url(request, vertex),
            )
            for vertex, release in vertices
        ]
    )
