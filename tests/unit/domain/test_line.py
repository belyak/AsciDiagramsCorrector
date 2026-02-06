"""Unit tests for Line entity."""

import pytest

from ascii_corrector.domain.cell import Cell
from ascii_corrector.domain.enums import Direction
from ascii_corrector.domain.line import Line
from ascii_corrector.domain.position import Position


class TestLineCreation:
    """Tests for Line creation."""

    def test_create_horizontal_line(self) -> None:
        """Should create a horizontal line from cells."""
        cells = [
            Cell.from_value("-", row=0, col=0),
            Cell.from_value("-", row=0, col=1),
            Cell.from_value("-", row=0, col=2),
        ]

        line = Line(cells=cells, direction=Direction.HORIZONTAL)

        assert line.direction == Direction.HORIZONTAL
        assert len(line.cells) == 3

    def test_create_vertical_line(self) -> None:
        """Should create a vertical line from cells."""
        cells = [
            Cell.from_value("|", row=0, col=0),
            Cell.from_value("|", row=1, col=0),
            Cell.from_value("|", row=2, col=0),
        ]

        line = Line(cells=cells, direction=Direction.VERTICAL)

        assert line.direction == Direction.VERTICAL


class TestLinePositions:
    """Tests for Line position methods."""

    def test_start_position_horizontal(self) -> None:
        """Start position should be leftmost cell for horizontal line."""
        cells = [
            Cell.from_value("-", row=5, col=3),
            Cell.from_value("-", row=5, col=4),
            Cell.from_value("-", row=5, col=5),
        ]
        line = Line(cells=cells, direction=Direction.HORIZONTAL)

        assert line.start_position() == Position(row=5, col=3)

    def test_end_position_horizontal(self) -> None:
        """End position should be rightmost cell for horizontal line."""
        cells = [
            Cell.from_value("-", row=5, col=3),
            Cell.from_value("-", row=5, col=4),
            Cell.from_value("-", row=5, col=5),
        ]
        line = Line(cells=cells, direction=Direction.HORIZONTAL)

        assert line.end_position() == Position(row=5, col=5)

    def test_start_position_vertical(self) -> None:
        """Start position should be topmost cell for vertical line."""
        cells = [
            Cell.from_value("|", row=2, col=5),
            Cell.from_value("|", row=3, col=5),
            Cell.from_value("|", row=4, col=5),
        ]
        line = Line(cells=cells, direction=Direction.VERTICAL)

        assert line.start_position() == Position(row=2, col=5)

    def test_end_position_vertical(self) -> None:
        """End position should be bottommost cell for vertical line."""
        cells = [
            Cell.from_value("|", row=2, col=5),
            Cell.from_value("|", row=3, col=5),
            Cell.from_value("|", row=4, col=5),
        ]
        line = Line(cells=cells, direction=Direction.VERTICAL)

        assert line.end_position() == Position(row=4, col=5)


class TestLineLength:
    """Tests for Line.length() method."""

    def test_length_returns_cell_count(self) -> None:
        """Length should return number of cells."""
        cells = [Cell.from_value("-", row=0, col=i) for i in range(5)]
        line = Line(cells=cells, direction=Direction.HORIZONTAL)

        assert line.length() == 5

    def test_length_empty_line(self) -> None:
        """Empty line should have length 0."""
        line = Line(cells=[], direction=Direction.HORIZONTAL)

        assert line.length() == 0


class TestLineDominantPosition:
    """Tests for dominant_row() and dominant_col() methods."""

    def test_dominant_row_for_horizontal_line(self) -> None:
        """Horizontal line should have a dominant row."""
        cells = [
            Cell.from_value("-", row=5, col=0),
            Cell.from_value("-", row=5, col=1),
            Cell.from_value("-", row=5, col=2),
        ]
        line = Line(cells=cells, direction=Direction.HORIZONTAL)

        assert line.dominant_row() == 5

    def test_dominant_col_for_vertical_line(self) -> None:
        """Vertical line should have a dominant column."""
        cells = [
            Cell.from_value("|", row=0, col=3),
            Cell.from_value("|", row=1, col=3),
            Cell.from_value("|", row=2, col=3),
        ]
        line = Line(cells=cells, direction=Direction.VERTICAL)

        assert line.dominant_col() == 3

    def test_dominant_row_for_vertical_returns_none(self) -> None:
        """Vertical line should not have a dominant row."""
        cells = [
            Cell.from_value("|", row=0, col=3),
            Cell.from_value("|", row=1, col=3),
        ]
        line = Line(cells=cells, direction=Direction.VERTICAL)

        assert line.dominant_row() is None

    def test_dominant_col_for_horizontal_returns_none(self) -> None:
        """Horizontal line should not have a dominant column."""
        cells = [
            Cell.from_value("-", row=5, col=0),
            Cell.from_value("-", row=5, col=1),
        ]
        line = Line(cells=cells, direction=Direction.HORIZONTAL)

        assert line.dominant_col() is None


class TestLineIsParallelTo:
    """Tests for Line.is_parallel_to() method."""

    def test_horizontal_lines_are_parallel(self) -> None:
        """Two horizontal lines should be parallel."""
        line1 = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(3)],
            direction=Direction.HORIZONTAL,
        )
        line2 = Line(
            cells=[Cell.from_value("-", row=2, col=i) for i in range(3)],
            direction=Direction.HORIZONTAL,
        )

        assert line1.is_parallel_to(line2) is True

    def test_vertical_lines_are_parallel(self) -> None:
        """Two vertical lines should be parallel."""
        line1 = Line(
            cells=[Cell.from_value("|", row=i, col=0) for i in range(3)],
            direction=Direction.VERTICAL,
        )
        line2 = Line(
            cells=[Cell.from_value("|", row=i, col=5) for i in range(3)],
            direction=Direction.VERTICAL,
        )

        assert line1.is_parallel_to(line2) is True

    def test_perpendicular_lines_not_parallel(self) -> None:
        """Horizontal and vertical lines should not be parallel."""
        line1 = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(3)],
            direction=Direction.HORIZONTAL,
        )
        line2 = Line(
            cells=[Cell.from_value("|", row=i, col=0) for i in range(3)],
            direction=Direction.VERTICAL,
        )

        assert line1.is_parallel_to(line2) is False


class TestLineOffset:
    """Tests for Line.offset_from() method."""

    def test_offset_between_horizontal_lines(self) -> None:
        """Should calculate row offset between horizontal lines."""
        line1 = Line(
            cells=[Cell.from_value("-", row=2, col=i) for i in range(3)],
            direction=Direction.HORIZONTAL,
        )
        line2 = Line(
            cells=[Cell.from_value("-", row=5, col=i) for i in range(3)],
            direction=Direction.HORIZONTAL,
        )

        assert line1.offset_from(line2) == -3
        assert line2.offset_from(line1) == 3

    def test_offset_between_vertical_lines(self) -> None:
        """Should calculate column offset between vertical lines."""
        line1 = Line(
            cells=[Cell.from_value("|", row=i, col=2) for i in range(3)],
            direction=Direction.VERTICAL,
        )
        line2 = Line(
            cells=[Cell.from_value("|", row=i, col=5) for i in range(3)],
            direction=Direction.VERTICAL,
        )

        assert line1.offset_from(line2) == -3
        assert line2.offset_from(line1) == 3

    def test_offset_same_position(self) -> None:
        """Offset should be 0 for lines at same position."""
        line1 = Line(
            cells=[Cell.from_value("-", row=5, col=0)],
            direction=Direction.HORIZONTAL,
        )
        line2 = Line(
            cells=[Cell.from_value("-", row=5, col=5)],
            direction=Direction.HORIZONTAL,
        )

        assert line1.offset_from(line2) == 0
