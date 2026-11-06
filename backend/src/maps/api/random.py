from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import VertexLabel
from ..query import get_random_entity
from .dependencies import get_session
from .utility import get_vertex_url

router = APIRouter(prefix="/random", tags=["random"])

Session = Annotated[AsyncSession, Depends(get_session)]


async def redirect_to_random_entity(
    request: Request, session: AsyncSession, label: VertexLabel | None
) -> RedirectResponse:
    """
    Redirect to the entity endpoint of a random vertex, optionally with a given label.
    """
    if (vertex := await get_random_entity(session, label)) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No vertices found")
    url = get_vertex_url(request, vertex)
    return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/")
async def get_random(request: Request, session: Session) -> RedirectResponse:
    """
    Redirect to a random entity of any type.
    """
    return await redirect_to_random_entity(request, session, None)


@router.get("/artist/")
async def get_random_artist(request: Request, session: Session) -> RedirectResponse:
    return await redirect_to_random_entity(request, session, VertexLabel.ARTIST)


@router.get("/company/")
async def get_random_company(request: Request, session: Session) -> RedirectResponse:
    return await redirect_to_random_entity(request, session, VertexLabel.COMPANY)


@router.get("/master/")
async def get_random_master(request: Request, session: Session) -> RedirectResponse:
    return await redirect_to_random_entity(request, session, VertexLabel.MASTER)


@router.get("/release/")
async def get_random_release(request: Request, session: Session) -> RedirectResponse:
    return await redirect_to_random_entity(request, session, VertexLabel.RELEASE)


@router.get("/track/")
async def get_random_track(request: Request, session: Session) -> RedirectResponse:
    return await redirect_to_random_entity(request, session, VertexLabel.TRACK)
