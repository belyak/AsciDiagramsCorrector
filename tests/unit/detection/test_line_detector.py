"""Unit tests for LineDetector."""

import pytest

from ascii_corrector.detection.line_detector import LineDetector
from ascii_corrector.domain import Direction, Grid


class TestLineDetectorHorizontal:
    """Tests for horizontal line detection."""

    def test_detect_simple_horizontal_line(self) -> None:
        """Should detect a simple horizontal line."""
        grid = Grid.from_string("-----")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert len(lines) == 1
        assert lines[0].direction == Direction.HORIZONTAL
        assert lines[0].length() == 5

    def test_detect_horizontal_line_with_spaces(self) -> None:
        """Should detect horizontal line surrounded by spaces."""
        grid = Grid.from_string("  ---  ")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert len(lines) == 1
        assert lines[0].length() == 3

    def test_detect_multiple_horizontal_lines(self) -> None:
        """Should detect multiple horizontal lines."""
        grid = Grid.from_string("---\n   \n---")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        horizontal = [ln for ln in lines if ln.direction == Direction.HORIZONTAL]
        assert len(horizontal) == 2

    def test_detect_horizontal_line_different_chars(self) -> None:
        """Should detect lines with different horizontal characters."""
        grid = Grid.from_string("===")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert len(lines) == 1
        assert lines[0].cells[0].character.value == "="

    def test_ignore_short_horizontal_sequences(self) -> None:
        """Should ignore sequences shorter than min_length."""
        grid = Grid.from_string("--")
        detector = LineDetector(min_line_length=3)

        lines = detector.detect_lines(grid)

        assert len(lines) == 0


class TestLineDetectorVertical:
    """Tests for vertical line detection."""

    def test_detect_simple_vertical_line(self) -> None:
        """Should detect a simple vertical line."""
        grid = Grid.from_string("|\n|\n|")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert len(lines) == 1
        assert lines[0].direction == Direction.VERTICAL
        assert lines[0].length() == 3

    def test_detect_vertical_line_with_spaces(self) -> None:
        """Should detect vertical line with surrounding spaces."""
        grid = Grid.from_string("  |  \n  |  \n  |  ")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        assert len(vertical) == 1
        assert vertical[0].length() == 3

    def test_detect_multiple_vertical_lines(self) -> None:
        """Should detect multiple vertical lines."""
        grid = Grid.from_string("|   |\n|   |\n|   |")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        assert len(vertical) == 2


class TestLineDetectorBox:
    """Tests for detecting lines in box structures."""

    def test_detect_box_lines(self) -> None:
        """Should detect all lines of a simple box."""
        # Use a taller box so vertical lines have length >= 2
        grid = Grid.from_string("+---+\n|   |\n|   |\n+---+")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        horizontal = [ln for ln in lines if ln.direction == Direction.HORIZONTAL]
        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]

        assert len(horizontal) == 2  # top and bottom
        assert len(vertical) == 2  # left and right

    def test_detect_small_box_with_min_length_1(self) -> None:
        """Should detect lines in small box with min_length=1."""
        grid = Grid.from_string("+---+\n|   |\n+---+")
        detector = LineDetector(min_line_length=1)

        lines = detector.detect_lines(grid)

        horizontal = [ln for ln in lines if ln.direction == Direction.HORIZONTAL]
        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]

        assert len(horizontal) == 2  # top and bottom
        assert len(vertical) == 2  # left and right (each 1 char)

    def test_detect_nested_box_lines(self) -> None:
        """Should detect lines in nested boxes."""
        # Nested box with sufficient height for vertical line detection
        grid = Grid.from_string("+-------+\n| +---+ |\n| |   | |\n| |   | |\n| +---+ |\n+-------+")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        horizontal = [ln for ln in lines if ln.direction == Direction.HORIZONTAL]
        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]

        # Outer: 2 horizontal (top/bottom), 2 vertical (left/right sides)
        # Inner: 2 horizontal (top/bottom), 2 vertical (left/right sides)
        assert len(horizontal) >= 4
        assert len(vertical) >= 4


class TestLineDetectorEdgeCases:
    """Tests for edge cases in line detection."""

    def test_empty_grid(self) -> None:
        """Should return empty list for empty grid."""
        grid = Grid.from_string("")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert lines == []

    def test_whitespace_only_grid(self) -> None:
        """Should return empty list for whitespace-only grid."""
        grid = Grid.from_string("     \n     ")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert lines == []

    def test_text_only_grid(self) -> None:
        """Should return empty list for text-only grid."""
        grid = Grid.from_string("hello\nworld")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert lines == []

    def test_single_line_character(self) -> None:
        """Single character should not be detected as line."""
        grid = Grid.from_string("-")
        detector = LineDetector(min_line_length=2)

        lines = detector.detect_lines(grid)

        assert lines == []


class TestLineDetectorPositions:
    """Tests for correct position detection."""

    def test_horizontal_line_positions(self) -> None:
        """Should correctly track positions of horizontal line."""
        grid = Grid.from_string("  ---  ")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        assert len(lines) == 1
        line = lines[0]
        assert line.start_position().col == 2
        assert line.end_position().col == 4
        assert line.dominant_row() == 0

    def test_vertical_line_positions(self) -> None:
        """Should correctly track positions of vertical line."""
        grid = Grid.from_string("  |  \n  |  \n  |  ")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        assert len(vertical) == 1
        line = vertical[0]
        assert line.start_position().row == 0
        assert line.end_position().row == 2
        assert line.dominant_col() == 2


class TestLineDetectorBridging:
    """Tests for + bridging behavior in line detection."""

    def test_vertical_line_bridges_through_plus(self) -> None:
        """Vertical line should bridge through + corners."""
        grid = Grid.from_string("+\n|\n|\n+")
        detector = LineDetector(min_line_length=2)

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        assert len(vertical) == 1
        assert vertical[0].length() == 2  # Only | cells, not +

    def test_vertical_bridge_single_pipe_between_corners(self) -> None:
        """Single pipe between corners should be detected with min_line_length=1."""
        grid = Grid.from_string("+\n|\n+")
        detector = LineDetector(min_line_length=1)

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        assert len(vertical) == 1
        assert vertical[0].length() == 1

    def test_bridge_does_not_include_plus_in_cells(self) -> None:
        """Bridging through + should not include + in line cells."""
        grid = Grid.from_string("+\n|\n|\n+\n|\n|\n+")
        detector = LineDetector(min_line_length=2)

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        assert len(vertical) == 1
        assert vertical[0].length() == 4  # 4 pipe cells
        for cell in vertical[0].cells:
            assert cell.character.value == "|"

    def test_horizontal_line_bridges_through_plus(self) -> None:
        """Horizontal line should bridge through + corners."""
        grid = Grid.from_string("+--+--+")
        detector = LineDetector(min_line_length=2)

        lines = detector.detect_lines(grid)

        horizontal = [ln for ln in lines if ln.direction == Direction.HORIZONTAL]
        assert len(horizontal) == 1
        assert horizontal[0].length() == 4  # Only - cells
        for cell in horizontal[0].cells:
            assert cell.character.value == "-"

    def test_no_bridge_when_only_corners(self) -> None:
        """Column of only + chars should not produce vertical lines."""
        grid = Grid.from_string("+\n+\n+")
        detector = LineDetector(min_line_length=1)

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        assert len(vertical) == 0

    def test_bridge_stops_at_space(self) -> None:
        """Bridge should not span across a space."""
        grid = Grid.from_string("|\n+\n \n|")
        detector = LineDetector(min_line_length=1)

        lines = detector.detect_lines(grid)

        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]
        # Each | is isolated: first | has + below but space after, second | is alone
        # With bridging, first segment is |,+ but + has space after -> line is just |
        # Second | is alone -> line of length 1
        assert len(vertical) == 2
        assert all(v.length() == 1 for v in vertical)

    def test_existing_box_detection_unchanged(self) -> None:
        """Box detection should still work correctly with bridging."""
        grid = Grid.from_string("+---+\n|   |\n|   |\n+---+")
        detector = LineDetector()

        lines = detector.detect_lines(grid)

        horizontal = [ln for ln in lines if ln.direction == Direction.HORIZONTAL]
        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]

        assert len(horizontal) == 2  # top and bottom
        assert len(vertical) == 2  # left and right
