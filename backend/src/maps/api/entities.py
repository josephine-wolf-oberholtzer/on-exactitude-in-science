from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import VertexLabel, VertexLabelName
from ..query import get_vertex
from .dependencies import get_session
from .utility import get_vertex_url

router = APIRouter(prefix="/entity", tags=["entity"])

Session = Annotated[AsyncSession, Depends(get_session)]


class EntityResponse(BaseModel):
    id: int
    index: int
    label: str
    name: str
    url: str


@router.get("/")
async def get_entity(
    request: Request,
    session: Session,
    id: int,
    label: VertexLabelName,
    index: int = 0,
) -> EntityResponse:
    """
    Look up a single entity by its ID and label.

    Most entities have an index of 0. A track shares its release's ID, so the
    index picks out the track.
    """
    if (
        vertex := await get_vertex(session, id, VertexLabel[label.name], index)
    ) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No {label.value} {id}")
    return EntityResponse(
        id=vertex.eid,
        index=vertex.index,
        label=VertexLabel(vertex.label).name.lower(),
        name=vertex.name,
        url=get_vertex_url(request, vertex),
    )
