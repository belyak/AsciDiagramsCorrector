"""Unit tests for box detection."""

import pytest

from ascii_corrector.detection.box_detector import BoxDetector, BoxStructure
from ascii_corrector.domain import Direction, Grid


class TestBoxDetectorBasic:
    """Basic box detection tests."""

    def test_detect_simple_box(self) -> None:
        """Should detect a simple rectangular box."""
        content = "+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1
        assert boxes[0].height == 3
        assert boxes[0].width == 4

    def test_detect_tall_box(self) -> None:
        """Should detect tall box with height > 2."""
        content = "+------+\n|      |\n|      |\n|      |\n|      |\n+------+"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1
        assert boxes[0].height == 6
        assert boxes[0].width == 8

    def test_detect_wide_box(self) -> None:
        """Should detect wide box."""
        content = "+----------+\n|          |\n+----------+"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1
        assert boxes[0].height == 3
        assert boxes[0].width == 12

    def test_detect_no_boxes_in_text(self) -> None:
        """Should return empty list for text without boxes."""
        content = "This is just text\nNo boxes here"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 0

    def test_detect_no_boxes_missing_corner(self) -> None:
        """Should return empty list when corner is missing."""
        content = "+--+\n|  |\n+-- "
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 0


class TestBoxDetectorMultipleBoxes:
    """Tests for detecting multiple boxes."""

    def test_detect_two_side_by_side_boxes(self) -> None:
        """Should detect two boxes next to each other."""
        content = "+--+  +--+\n|  |  |  |\n+--+  +--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 2

    def test_detect_two_stacked_boxes(self) -> None:
        """Should detect two boxes stacked vertically."""
        content = "+--+\n|  |\n+--+\n\n+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 2


class TestBoxDetectorUnicode:
    """Tests for Unicode box characters."""

    def test_detect_unicode_box(self) -> None:
        """Should detect box with Unicode corners."""
        content = "┌──┐\n│  │\n└──┘"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1
        assert boxes[0].height == 3
        assert boxes[0].width == 4

    def test_detect_heavy_unicode_box(self) -> None:
        """Should detect box with heavy Unicode corners."""
        content = "╔══╗\n║  ║\n╚══╝"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1

    def test_detect_unicode_tall_box(self) -> None:
        """Should detect tall Unicode box."""
        content = "┌────┐\n│    │\n│    │\n│    │\n│    │\n└────┘"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1
        assert boxes[0].height == 6
        assert boxes[0].width == 6


class TestBoxStructure:
    """Tests for BoxStructure properties."""

    def test_box_edges_have_correct_direction(self) -> None:
        """Box edges should have correct directions."""
        content = "+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1
        box = boxes[0]
        assert box.top_line.direction == Direction.HORIZONTAL
        assert box.bottom_line.direction == Direction.HORIZONTAL
        assert box.left_line.direction == Direction.VERTICAL
        assert box.right_line.direction == Direction.VERTICAL

    def test_box_edges_have_correct_positions(self) -> None:
        """Box edges should be at correct positions."""
        content = "+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()

        boxes = detector.detect_boxes(grid)

        assert len(boxes) == 1
        box = boxes[0]
        # Top edge at row 0
        assert box.top_line.dominant_row() == 0
        # Bottom edge at row 2
        assert box.bottom_line.dominant_row() == 2
        # Left edge at col 0
        assert box.left_line.dominant_col() == 0
        # Right edge at col 3
        assert box.right_line.dominant_col() == 3
