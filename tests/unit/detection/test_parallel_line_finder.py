"""Unit tests for ParallelLineFinder."""

import pytest

from ascii_corrector.detection.line_detector import LineDetector
from ascii_corrector.detection.parallel_line_finder import ParallelLineFinder
from ascii_corrector.domain import Cell, Direction, Grid, Line


class TestParallelLineFinderHorizontal:
    """Tests for finding parallel horizontal lines."""

    def test_find_distant_horizontal_lines_separate(self) -> None:
        """Should NOT group horizontal lines far apart (top/bottom of box)."""
        # Two horizontal lines at rows 0 and 2 - too far apart to be "shifted"
        grid = Grid.from_string("-----\n     \n-----")
        detector = LineDetector()
        finder = ParallelLineFinder(tolerance=1)

        lines = detector.detect_lines(grid)
        groups = finder.find_parallel_groups(lines)

        # Should find two separate groups (lines are 2 rows apart, > tolerance)
        horizontal_groups = [g for g in groups if g.direction == Direction.HORIZONTAL]
        assert len(horizontal_groups) == 2

    def test_find_adjacent_horizontal_lines_grouped(self) -> None:
        """Should group horizontal lines within tolerance."""
        # Two horizontal lines at rows 0 and 1 - within tolerance
        grid = Grid.from_string("-----\n-----")
        detector = LineDetector()
        finder = ParallelLineFinder(tolerance=1)

        lines = detector.detect_lines(grid)
        groups = finder.find_parallel_groups(lines)

        # Should find one group (lines are 1 row apart, within tolerance)
        horizontal_groups = [g for g in groups if g.direction == Direction.HORIZONTAL]
        assert len(horizontal_groups) == 1
        assert len(horizontal_groups[0].lines) == 2

    def test_find_shifted_horizontal_lines(self) -> None:
        """Should group lines that are slightly shifted."""
        # Create lines manually - one at row 0, one at row 1 (shifted)
        line1 = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        line2 = Line(
            cells=[Cell.from_value("-", row=1, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )

        finder = ParallelLineFinder(tolerance=1)
        groups = finder.find_parallel_groups([line1, line2])

        # Should group them together since they're within tolerance
        assert len(groups) == 1
        assert len(groups[0].lines) == 2

    def test_separate_distant_horizontal_lines(self) -> None:
        """Should not group lines that are far apart."""
        # Lines at row 0 and row 10
        line1 = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        line2 = Line(
            cells=[Cell.from_value("-", row=10, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )

        finder = ParallelLineFinder(tolerance=1)
        groups = finder.find_parallel_groups([line1, line2])

        # Should be separate groups
        assert len(groups) == 2


class TestParallelLineFinderVertical:
    """Tests for finding parallel vertical lines."""

    def test_find_distant_vertical_lines_separate(self) -> None:
        """Should NOT group vertical lines far apart (left/right of box)."""
        grid = Grid.from_string("|   |\n|   |\n|   |")
        detector = LineDetector()
        finder = ParallelLineFinder(tolerance=1)

        lines = detector.detect_lines(grid)
        groups = finder.find_parallel_groups(lines)

        # Should find two separate groups (columns 0 and 4, > tolerance)
        vertical_groups = [g for g in groups if g.direction == Direction.VERTICAL]
        assert len(vertical_groups) == 2

    def test_find_adjacent_vertical_lines_grouped(self) -> None:
        """Should group vertical lines within tolerance."""
        grid = Grid.from_string("||\n||\n||")
        detector = LineDetector()
        finder = ParallelLineFinder(tolerance=1)

        lines = detector.detect_lines(grid)
        groups = finder.find_parallel_groups(lines)

        # Should find one group (columns 0 and 1, within tolerance)
        vertical_groups = [g for g in groups if g.direction == Direction.VERTICAL]
        assert len(vertical_groups) == 1
        assert len(vertical_groups[0].lines) == 2

    def test_find_shifted_vertical_lines(self) -> None:
        """Should group vertical lines that are slightly shifted."""
        # Create lines at col 0 and col 1 (shifted)
        line1 = Line(
            cells=[Cell.from_value("|", row=i, col=0) for i in range(5)],
            direction=Direction.VERTICAL,
        )
        line2 = Line(
            cells=[Cell.from_value("|", row=i, col=1) for i in range(5)],
            direction=Direction.VERTICAL,
        )

        finder = ParallelLineFinder(tolerance=1)
        groups = finder.find_parallel_groups([line1, line2])

        # Should group them together
        assert len(groups) == 1
        assert len(groups[0].lines) == 2


class TestParallelLineFinderMixed:
    """Tests for mixed horizontal and vertical lines."""

    def test_separate_horizontal_and_vertical(self) -> None:
        """Should not group horizontal with vertical lines."""
        h_line = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        v_line = Line(
            cells=[Cell.from_value("|", row=i, col=0) for i in range(5)],
            direction=Direction.VERTICAL,
        )

        finder = ParallelLineFinder()
        groups = finder.find_parallel_groups([h_line, v_line])

        # Should be in separate groups by direction
        h_groups = [g for g in groups if g.direction == Direction.HORIZONTAL]
        v_groups = [g for g in groups if g.direction == Direction.VERTICAL]

        assert len(h_groups) == 1
        assert len(v_groups) == 1


class TestParallelLineFinderReferenceSelection:
    """Tests for reference line selection."""

    def test_reference_line_is_longest(self) -> None:
        """Reference line should be the longest in the group."""
        # Short line at row 0, long line at row 1
        short_line = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(3)],
            direction=Direction.HORIZONTAL,
        )
        long_line = Line(
            cells=[Cell.from_value("-", row=1, col=i) for i in range(10)],
            direction=Direction.HORIZONTAL,
        )

        finder = ParallelLineFinder(tolerance=1)
        groups = finder.find_parallel_groups([short_line, long_line])

        assert len(groups) == 1
        assert groups[0].reference_line == long_line


class TestParallelLineFinderEdgeCases:
    """Tests for edge cases."""

    def test_empty_lines_list(self) -> None:
        """Should return empty list for no lines."""
        finder = ParallelLineFinder()
        groups = finder.find_parallel_groups([])

        assert groups == []

    def test_single_line(self) -> None:
        """Single line should form its own group."""
        line = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )

        finder = ParallelLineFinder()
        groups = finder.find_parallel_groups([line])

        assert len(groups) == 1
        assert len(groups[0].lines) == 1
