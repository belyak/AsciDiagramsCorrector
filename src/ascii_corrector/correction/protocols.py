"""Protocol definitions for correction layer."""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from ascii_corrector.detection.protocols import ParallelGroup
from ascii_corrector.domain import Grid, Line


@dataclass
class ShiftCorrection:
    """Represents a correction to be applied to a line."""

    line: Line
    row_offset: int = 0
    col_offset: int = 0
    confidence: float = 1.0


@dataclass
class AlignmentResult:
    """Result of alignment calculation for a parallel group."""

    group: ParallelGroup
    corrections: list[ShiftCorrection] = field(default_factory=list)
    reference_position: int | None = None


@dataclass
class CorrectionResult:
    """Result of the full correction process."""

    original_grid: Grid
    corrected_grid: Grid
    corrections_applied: list[ShiftCorrection] = field(default_factory=list)
    groups_found: list[ParallelGroup] = field(default_factory=list)

    @property
    def corrections_count(self) -> int:
        """Number of corrections applied."""
        return len(self.corrections_applied)


@runtime_checkable
class AlignmentCalculatorProtocol(Protocol):
    """Protocol for calculating alignment corrections."""

    def calculate_alignment(self, group: ParallelGroup) -> AlignmentResult:
        """Calculate how to align lines in a parallel group."""
        ...


@runtime_checkable
class ShiftCorrectorProtocol(Protocol):
    """Protocol for applying shift corrections."""

    def apply_correction(
        self,
        correction: ShiftCorrection,
        grid: Grid,
    ) -> Grid:
        """Apply a shift correction to the grid."""
        ...


@runtime_checkable
class StrayCharacterFinderProtocol(Protocol):
    """Protocol for finding stray line characters not part of detected lines."""

    def find_stray_corrections(
        self, grid: Grid, detected_lines: list[Line]
    ) -> list[ShiftCorrection]:
        """Find corrections for stray characters near detected lines."""
        ...


@runtime_checkable
class RowShiftCorrectorProtocol(Protocol):
    """Protocol for detecting and correcting whole-row shifts."""

    def find_row_shift_corrections(
        self, grid: Grid
    ) -> list[ShiftCorrection]:
        """Find corrections for rows shifted by a consistent column offset."""
        ...


@runtime_checkable
class CorrectionEngineProtocol(Protocol):
    """Protocol for the main correction orchestrator."""

    def correct(self, grid: Grid) -> CorrectionResult:
        """Apply all corrections to a grid."""
        ...
