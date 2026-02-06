"""Custom exception hierarchy for ASCII Diagram Corrector."""

from typing import Any


class AsciiCorrectorError(Exception):
    """Base exception for all ASCII Corrector errors."""

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.context = context


class DiagramParseError(AsciiCorrectorError):
    """Error parsing ASCII diagram input."""


class InvalidGridError(AsciiCorrectorError):
    """Error with grid structure or dimensions."""


class LineDetectionError(AsciiCorrectorError):
    """Error during line detection phase."""


class CorrectionError(AsciiCorrectorError):
    """Error applying corrections to diagram."""


class CollisionError(CorrectionError):
    """Shift would cause character collision."""


class BoundsError(CorrectionError):
    """Shift would move characters out of bounds."""


class ConfigurationError(AsciiCorrectorError):
    """Error in configuration or settings."""


class DiagramIOError(AsciiCorrectorError):
    """Error reading or writing diagram files."""


class MarkdownParseError(AsciiCorrectorError):
    """Error parsing Markdown document structure."""


class BackupError(AsciiCorrectorError):
    """Error creating backup files."""
