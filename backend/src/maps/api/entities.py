from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Vertex, VertexLabel
from .dependencies import get_session

router = APIRouter(prefix="/entity", tags=["entity"])

Session = Annotated[AsyncSession, Depends(get_session)]


class EntityResponse(BaseModel):
    id: int
    index: int
    label: str


async def get_entity(
    session: AsyncSession, *, id: int, index: int, label: VertexLabel
) -> EntityResponse:
    """
    Look up a single vertex by its primary key.
    """
    vertex = await session.scalar(
        select(Vertex).where(
            Vertex.id == id, Vertex.label == int(label), Vertex.index == index
        )
    )
    if vertex is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No {label.name.lower()} {id}")
    return EntityResponse(
        id=vertex.id, index=vertex.index, label=VertexLabel(vertex.label).name.lower()
    )


@router.get("/artist/{id}")
async def entity_artist(id: int, session: Session) -> EntityResponse:
    return await get_entity(session, id=id, index=0, label=VertexLabel.ARTIST)


@router.get("/company/{id}")
async def entity_company(id: int, session: Session) -> EntityResponse:
    return await get_entity(session, id=id, index=0, label=VertexLabel.COMPANY)


@router.get("/master/{id}")
async def entity_master(id: int, session: Session) -> EntityResponse:
    return await get_entity(session, id=id, index=0, label=VertexLabel.MASTER)


@router.get("/release/{id}")
async def entity_release(id: int, session: Session) -> EntityResponse:
    return await get_entity(session, id=id, index=0, label=VertexLabel.RELEASE)


@router.get("/release/{id}/track/{index}")
async def entity_track(id: int, index: int, session: Session) -> EntityResponse:
    # A track shares its release's ID, so the index picks out the track
    return await get_entity(session, id=id, index=index, label=VertexLabel.TRACK)
