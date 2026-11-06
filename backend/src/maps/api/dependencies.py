from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """
    Yield a session bound to the app's engine.
    """
    async with AsyncSession(
        request.app.state.engine, expire_on_commit=False
    ) as session:
        yield session
