from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..constants import VertexLabel, VertexLabelName
from ..query import get_random_vertex
from .dependencies import get_session
from .utility import get_vertex_url

router = APIRouter(prefix="/random", tags=["random"])

Session = Annotated[AsyncSession, Depends(get_session)]


async def redirect_to_random_entity(
    request: Request, session: AsyncSession, label: VertexLabel | None = None
) -> RedirectResponse:
    """
    Redirect to the entity endpoint of a random vertex, optionally with a given label.
    """
    if (vertex := await get_random_vertex(session, label)) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No vertices found")
    url = get_vertex_url(request, vertex)
    return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/")
async def get_random_entity(
    request: Request, session: Session, label: VertexLabelName | None = None
) -> RedirectResponse:
    """
    Redirect to a random entity, optionally restricted by label.
    """
    return await redirect_to_random_entity(
        request, session, VertexLabel[label.name] if label else None
    )
