"""Protocol definitions for detection layer."""

from typing import Protocol, runtime_checkable

from ascii_corrector.domain import CharacterClass, Grid, Line


@runtime_checkable
class CharacterClassifierProtocol(Protocol):
    """Protocol for character classification."""

    def classify(self, char: str) -> CharacterClass:
        """Classify a single character."""
        ...


@runtime_checkable
class LineDetectorProtocol(Protocol):
    """Protocol for line detection in grids."""

    def detect_lines(self, grid: Grid) -> list[Line]:
        """Detect all lines in the grid."""
        ...


@runtime_checkable
class ParallelFinderProtocol(Protocol):
    """Protocol for finding parallel line groups."""

    def find_parallel_groups(self, lines: list[Line]) -> list["ParallelGroup"]:
        """Group lines that should be parallel."""
        ...


from dataclasses import dataclass, field

from ascii_corrector.domain.enums import Direction


@dataclass
class ParallelGroup:
    """Group of lines that should be parallel/aligned."""

    lines: list[Line] = field(default_factory=list)
    direction: Direction = Direction.HORIZONTAL
    reference_line: Line | None = None
    expected_position: int | None = None  # Expected row (horizontal) or col (vertical)
