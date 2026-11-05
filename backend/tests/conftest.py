import datetime
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from maps.etl import Artist, Company, Master, Release
from maps.models import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.community.postgres import PostgresContainer


@pytest.fixture(autouse=True, scope="session")
def database_container(request):
    def stop():
        postgres.stop()

    postgres = PostgresContainer("postgres:16-alpine")
    postgres.start()
    request.addfinalizer(stop)

    alembic_config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    alembic_config.set_main_option(
        "sqlalchemy.url", postgres.get_connection_url(driver="asyncpg")
    )
    command.upgrade(alembic_config, "head")
    return postgres


@pytest_asyncio.fixture
async def engine(database_container: PostgresContainer) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        database_container.get_connection_url(driver="asyncpg")
    )
    yield engine
    async with engine.begin() as connection:
        table_names = ", ".join(
            f'"{table.name}"' for table in Base.metadata.sorted_tables
        )
        await connection.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY"))
    await engine.dispose()


@pytest.fixture
def artists_iterator(artists_xml_path: Path) -> Iterator[Artist]:
    return Artist.iterate_xml(artists_xml_path)


@pytest.fixture
def artists_xml_path(xml_directory_path: Path) -> Path:
    return xml_directory_path / "discogs_test_artists.xml.gz"


@pytest.fixture
def companies_iterator(companies_xml_path: Path) -> Iterator[Company]:
    return Company.iterate_xml(companies_xml_path)


@pytest.fixture
def companies_xml_path(xml_directory_path: Path) -> Path:
    # N.B. Discogs uses the term "labels" but this is imprecise, as the entity
    # actually refers to any company.
    return xml_directory_path / "discogs_test_labels.xml.gz"


@pytest.fixture
def masters_iterator(masters_xml_path: Path) -> Iterator[Master]:
    return Master.iterate_xml(masters_xml_path)


@pytest.fixture
def masters_xml_path(xml_directory_path: Path) -> Path:
    return xml_directory_path / "discogs_test_masters.xml.gz"


@pytest.fixture
def releases_iterator(releases_xml_path: Path) -> Iterator[Release]:
    return Release.iterate_xml(releases_xml_path)


@pytest.fixture
def releases_xml_path(xml_directory_path: Path) -> Path:
    return xml_directory_path / "discogs_test_releases.xml.gz"


@pytest.fixture
def today() -> datetime.date:
    return datetime.date.today()


@pytest.fixture
def xml_directory_path() -> Path:
    return Path(__file__).parent / "data"
