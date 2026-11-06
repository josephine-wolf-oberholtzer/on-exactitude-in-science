import dataclasses
import datetime
import json
import os
from pathlib import Path
from typing import ClassVar, Self


@dataclasses.dataclass(frozen=True)
class Checkpoint:
    """
    The last entity committed, and which entity type and dataset it belongs to.
    """

    FILE_NAME: ClassVar[str] = ".load-checkpoint.json"

    entity: str
    last_id: int
    dataset: datetime.date

    @classmethod
    def read(cls, path: Path) -> Self | None:
        """
        Read a checkpoint, treating a missing or unreadable file as no checkpoint.
        """
        try:
            data = json.loads(path.read_text())
            return cls(
                entity=data["entity"],
                last_id=int(data["last_id"]),
                dataset=datetime.date.fromisoformat(data["dataset"]),
            )
        except OSError, ValueError, KeyError, TypeError:
            return None

    def write(self, path: Path) -> None:
        """
        Atomically write the checkpoint, so a crash never leaves a partial file.
        """
        temporary_path = path.with_name(path.name + ".tmp")
        temporary_path.write_text(
            json.dumps(
                {
                    "entity": self.entity,
                    "last_id": self.last_id,
                    "dataset": self.dataset.isoformat(),
                }
            )
        )
        os.replace(temporary_path, path)

    @staticmethod
    def get_path(data_directory_path: Path) -> Path:
        return data_directory_path / Checkpoint.FILE_NAME

    @staticmethod
    def clear(path: Path) -> None:
        path.unlink(missing_ok=True)
