import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine

from .checkpoint import Checkpoint
from .entities import Artist, Company, Entity, Master, Release


async def load(
    data_directory_path: Path, limit: int | None, database_url: str, resume: bool
) -> None:
    engine = create_async_engine(database_url)
    logger = logging.getLogger("maps")
    entity_classes: list[type[Entity]] = [Artist, Company, Master, Release]
    # Limited runs are partial by design: no checkpoint is read or written.
    checkpoint_path = None if limit else Checkpoint.get_path(data_directory_path)
    if (
        saved := Checkpoint.read(checkpoint_path)
        if checkpoint_path and resume
        else None
    ) is not None:
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
                is_resumed = saved is not None and entity_class.__name__ == saved.entity
                await entity_class.load(
                    data_directory_path=data_directory_path,
                    connection=connection,
                    limit=limit,
                    checkpoint_path=checkpoint_path,
                    resume_after_id=saved.last_id if is_resumed and saved else None,
                )
            if checkpoint_path is not None:
                Checkpoint.clear(checkpoint_path)
    finally:
        await engine.dispose()
