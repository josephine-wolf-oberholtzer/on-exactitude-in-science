import asyncio
import logging
from pathlib import Path

import click
from sqlalchemy.ext.asyncio import create_async_engine

from . import checkpoint, config
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

    async def run() -> None:
        engine = create_async_engine(database_url)
        logger = logging.getLogger("maps")
        entity_classes = [Artist, Company, Master, Release]
        # Limited runs are partial by design: no checkpoint is read or written.
        checkpoint_path = None if limit else checkpoint.get_path(data_directory_path)
        saved = checkpoint.read(checkpoint_path) if checkpoint_path and resume else None
        if saved is not None:
            names = [c.__name__ for c in entity_classes]
            _, dataset = entity_classes[0].get_xml_path(data_directory_path)
            if saved.entity not in names or saved.dataset != dataset:
                logger.warning("Ignoring stale checkpoint: %s", saved)
                saved = None
            else:
                # Skip entity types completed before the crash
                entity_classes = entity_classes[names.index(saved.entity) :]
                logger.info("Resuming %s after entity %d", saved.entity, saved.last_id)
        try:
            async with engine.connect() as connection:
                for entity_class in entity_classes:
                    is_resumed = (
                        saved is not None and entity_class.__name__ == saved.entity
                    )
                    await entity_class.load(
                        data_directory_path=data_directory_path,
                        connection=connection,
                        limit=limit,
                        checkpoint_path=checkpoint_path,
                        resume_after_id=saved.last_id if is_resumed and saved else None,
                    )
                if checkpoint_path is not None:
                    checkpoint.clear(checkpoint_path)
        finally:
            await engine.dispose()

    asyncio.run(run())
