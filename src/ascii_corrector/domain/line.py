"""Line entity representing a sequence of connected cells."""

from __future__ import annotations

from dataclasses import dataclass, field

from ascii_corrector.domain.cell import Cell
from ascii_corrector.domain.enums import Direction
from ascii_corrector.domain.position import Position


@dataclass
class Line:
    """
    A line in the ASCII diagram.

    Represents a sequence of cells forming a horizontal or vertical line.
    Used for detecting parallel lines and calculating alignment corrections.
    """

    cells: list[Cell] = field(default_factory=list)
    direction: Direction = Direction.HORIZONTAL

    def start_position(self) -> Position:
        """
        Get the starting position of the line.

        For horizontal lines: leftmost position (min col).
        For vertical lines: topmost position (min row).

        Returns:
            Position of the line start.

        Raises:
            ValueError: If line has no cells.
        """
        if not self.cells:
            raise ValueError("Cannot get start position of empty line")

        if self.direction == Direction.HORIZONTAL:
            return min(self.cells, key=lambda c: c.position.col).position
        else:
            return min(self.cells, key=lambda c: c.position.row).position

    def end_position(self) -> Position:
        """
        Get the ending position of the line.

        For horizontal lines: rightmost position (max col).
        For vertical lines: bottommost position (max row).

        Returns:
            Position of the line end.

        Raises:
            ValueError: If line has no cells.
        """
        if not self.cells:
            raise ValueError("Cannot get end position of empty line")

        if self.direction == Direction.HORIZONTAL:
            return max(self.cells, key=lambda c: c.position.col).position
        else:
            return max(self.cells, key=lambda c: c.position.row).position

    def length(self) -> int:
        """
        Get the number of cells in the line.

        Returns:
            Number of cells.
        """
        return len(self.cells)

    def dominant_row(self) -> int | None:
        """
        Get the dominant row for horizontal lines.

        For horizontal lines, all cells should be on the same row.

        Returns:
            Row number for horizontal lines, None for vertical lines.
        """
        if self.direction != Direction.HORIZONTAL or not self.cells:
            return None
        return self.cells[0].position.row

    def dominant_col(self) -> int | None:
        """
        Get the dominant column for vertical lines.

        For vertical lines, all cells should be on the same column.

        Returns:
            Column number for vertical lines, None for horizontal lines.
        """
        if self.direction != Direction.VERTICAL or not self.cells:
            return None
        return self.cells[0].position.col

    def is_parallel_to(self, other: Line) -> bool:
        """
        Check if this line is parallel to another line.

        Lines are parallel if they have the same direction.

        Args:
            other: Line to compare with.

        Returns:
            True if lines are parallel.
        """
        return self.direction == other.direction

    def offset_from(self, other: Line) -> int:
        """
        Calculate the positional offset from another parallel line.

        For horizontal lines: difference in rows.
        For vertical lines: difference in columns.

        Args:
            other: Line to calculate offset from.

        Returns:
            Signed offset (positive = this line is below/right of other).
        """
        if self.direction == Direction.HORIZONTAL:
            self_row = self.dominant_row()
            other_row = other.dominant_row()
            if self_row is not None and other_row is not None:
                return self_row - other_row
        else:
            self_col = self.dominant_col()
            other_col = other.dominant_col()
            if self_col is not None and other_col is not None:
                return self_col - other_col
        return 0
