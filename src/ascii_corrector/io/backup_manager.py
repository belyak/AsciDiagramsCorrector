"""Backup manager for creating file backups before in-place modification."""

from __future__ import annotations

import shutil
from pathlib import Path

from ascii_corrector.exceptions import BackupError


class BackupManager:
    """Creates backup copies of files with incrementing suffixes."""

    def __init__(self, suffix: str = ".bak") -> None:
        self._suffix = suffix

    def create_backup(self, path: Path) -> Path:
        """Create a backup of the file at path.

        Returns the path to the backup file.
        Raises BackupError if the source file does not exist.
        """
        if not path.exists():
            raise BackupError(f"Cannot backup non-existent file: {path}", path=str(path))

        backup_path = path.parent / (path.name + self._suffix)

        if backup_path.exists():
            counter = 1
            while True:
                candidate = path.parent / f"{path.name}{self._suffix}.{counter}"
                if not candidate.exists():
                    backup_path = candidate
                    break
                counter += 1

        shutil.copy2(path, backup_path)
        return backup_path
