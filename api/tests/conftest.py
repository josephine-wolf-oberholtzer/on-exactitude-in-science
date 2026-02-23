import pytest_asyncio

from maps import goblin

pytest_plugins = "aiohttp.pytest_plugin"


@pytest_asyncio.fixture
async def goblin_app():
    async with goblin.GoblinManager(aliases={"g": "tg"}) as goblin_app:
        session = await goblin_app.session()
        await session.g.V().drop().toList()
        yield goblin_app
