import asyncio
import logging
from pathlib import Path

import click

from . import config
from .etl.loader import load as etl_load


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
@click.option(
    "--resume",
    is_flag=True,
    default=False,
    help="Resume from the checkpoint left by a crashed load, if there is one.",
)
def load(
    data_directory_path: Path, limit: int | None, database_url: str, resume: bool
) -> None:
    """
    Load Discogs XML archives into the database.
    """

    asyncio.run(
        etl_load(
            data_directory_path=data_directory_path,
            limit=limit,
            database_url=database_url,
            resume=resume,
        )
    )
