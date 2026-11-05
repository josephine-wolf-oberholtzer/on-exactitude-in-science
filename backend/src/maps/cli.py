import asyncio
import logging
from pathlib import Path

import click
from sqlalchemy.ext.asyncio import create_async_engine

from . import config
from .etl import Artist, Company, Master, Release


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    logging.getLogger("maps").setLevel(logging.INFO)


@cli.command()
@click.option(
    "--path",
    "data_directory_path",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing the Discogs XML archives.",
)
@click.option(
    "--limit",
    type=click.IntRange(min=1),
    default=None,
    help="Maximum number of entities to load for each entity type.",
)
@click.option(
    "--database-url",
    default=config.DATABASE_URL,
    show_default=False,
    help="SQLAlchemy URL of the database to load into",
)
def load(data_directory_path: Path, limit: int | None, database_url: str) -> None:
    """
    Load Discogs XML archives into the database.
    """

    async def run() -> None:
        engine = create_async_engine(database_url)
        try:
            async with engine.connect() as connection:
                for entity_class in (Artist, Company, Master, Release):
                    await entity_class.load(
                        data_directory_path=data_directory_path,
                        connection=connection,
                        limit=limit,
                    )
        finally:
            await engine.dispose()

    asyncio.run(run())
