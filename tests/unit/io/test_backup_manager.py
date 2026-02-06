"""Unit tests for BackupManager."""

import pytest

from ascii_corrector.exceptions import BackupError
from ascii_corrector.io.backup_manager import BackupManager


class TestBackupManagerBasic:
    """Basic backup creation tests."""

    def test_creates_backup_file(self, tmp_path) -> None:
        original = tmp_path / "doc.md"
        original.write_text("content")

        manager = BackupManager()
        backup_path = manager.create_backup(original)

        assert backup_path.exists()
        assert backup_path == tmp_path / "doc.md.bak"

    def test_backup_preserves_content(self, tmp_path) -> None:
        original = tmp_path / "doc.md"
        original.write_text("important content")

        manager = BackupManager()
        backup_path = manager.create_backup(original)

        assert backup_path.read_text() == "important content"

    def test_custom_suffix(self, tmp_path) -> None:
        original = tmp_path / "doc.md"
        original.write_text("content")

        manager = BackupManager(suffix=".backup")
        backup_path = manager.create_backup(original)

        assert backup_path == tmp_path / "doc.md.backup"


class TestBackupManagerIncrementing:
    """Tests for incrementing backup suffix."""

    def test_increments_when_backup_exists(self, tmp_path) -> None:
        original = tmp_path / "doc.md"
        original.write_text("v2")
        (tmp_path / "doc.md.bak").write_text("v1")

        manager = BackupManager()
        backup_path = manager.create_backup(original)

        assert backup_path == tmp_path / "doc.md.bak.1"
        assert backup_path.read_text() == "v2"

    def test_increments_multiple_times(self, tmp_path) -> None:
        original = tmp_path / "doc.md"
        original.write_text("v3")
        (tmp_path / "doc.md.bak").write_text("v1")
        (tmp_path / "doc.md.bak.1").write_text("v2")

        manager = BackupManager()
        backup_path = manager.create_backup(original)

        assert backup_path == tmp_path / "doc.md.bak.2"
        assert backup_path.read_text() == "v3"


class TestBackupManagerErrors:
    """Error handling tests."""

    def test_missing_file_raises_backup_error(self, tmp_path) -> None:
        missing = tmp_path / "nonexistent.md"

        manager = BackupManager()
        with pytest.raises(BackupError):
            manager.create_backup(missing)
