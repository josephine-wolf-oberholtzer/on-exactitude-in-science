import dataclasses
import datetime
import json
import os
from pathlib import Path

CHECKPOINT_FILE_NAME = ".load-checkpoint.json"


@dataclasses.dataclass(frozen=True)
class Checkpoint:
    """
    The last entity committed, and which entity type and dataset it belongs to.
    """

    entity: str
    last_id: int
    dataset: datetime.date


def get_path(data_directory_path: Path) -> Path:
    return data_directory_path / CHECKPOINT_FILE_NAME


def read(path: Path) -> Checkpoint | None:
    """
    Read a checkpoint, treating a missing or unreadable file as no checkpoint.
    """
    try:
        data = json.loads(path.read_text())
        return Checkpoint(
            entity=data["entity"],
            last_id=int(data["last_id"]),
            dataset=datetime.date.fromisoformat(data["dataset"]),
        )
    except OSError, ValueError, KeyError, TypeError:
        return None


def write(path: Path, checkpoint: Checkpoint) -> None:
    """
    Atomically write a checkpoint, so a crash never leaves a partial file.
    """
    temporary_path = path.with_name(path.name + ".tmp")
    temporary_path.write_text(
        json.dumps(
            {
                "entity": checkpoint.entity,
                "last_id": checkpoint.last_id,
                "dataset": checkpoint.dataset.isoformat(),
            }
        )
    )
    os.replace(temporary_path, path)


def clear(path: Path) -> None:
    path.unlink(missing_ok=True)
