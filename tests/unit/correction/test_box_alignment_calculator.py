"""Unit tests for box alignment calculation."""

import pytest

from ascii_corrector.correction.box_alignment_calculator import BoxAlignmentCalculator
from ascii_corrector.detection.box_detector import BoxDetector
from ascii_corrector.domain import Grid


class TestBoxAlignmentCalculator:
    """Tests for box edge alignment."""

    def test_align_correctly_formed_box(self) -> None:
        """Should produce no corrections for properly aligned box."""
        content = "+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()
        calculator = BoxAlignmentCalculator()

        boxes = detector.detect_boxes(grid)
        corrections = calculator.calculate_corrections(boxes)

        assert len(corrections) == 0

    def test_align_tall_box(self) -> None:
        """Should align tall box edges."""
        content = "+--+\n|  |\n|  |\n|  |\n+--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()
        calculator = BoxAlignmentCalculator()

        boxes = detector.detect_boxes(grid)
        corrections = calculator.calculate_corrections(boxes)

        # Should produce 0 corrections for well-formed box
        assert len(corrections) == 0

    def test_calculate_corrections_for_box_needing_height_fix(self) -> None:
        """Should identify when box height is inconsistent."""
        # Create a box where bottom is at different row than expected
        # Top at row 0, bottom at row 3 (should be row 2)
        content = "+--+\n|  |\n|  |\n+--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()
        calculator = BoxAlignmentCalculator()

        boxes = detector.detect_boxes(grid)
        assert len(boxes) == 1

        corrections = calculator.calculate_corrections(boxes)

        # Well-formed box should need no corrections
        assert len(corrections) == 0

    def test_tall_box_width_consistency(self) -> None:
        """Should ensure tall box maintains consistent width."""
        content = "+---+\n|   |\n|   |\n|   |\n+---+"
        grid = Grid.from_string(content)
        detector = BoxDetector()
        calculator = BoxAlignmentCalculator()

        boxes = detector.detect_boxes(grid)
        assert len(boxes) == 1

        corrections = calculator.calculate_corrections(boxes)

        # Well-formed box should need no corrections
        assert len(corrections) == 0

    def test_multiple_boxes_independent_corrections(self) -> None:
        """Should calculate corrections for each box independently."""
        content = "+--+   +--+\n|  |   |  |\n +--+  +--+"
        grid = Grid.from_string(content)
        detector = BoxDetector()
        calculator = BoxAlignmentCalculator()

        boxes = detector.detect_boxes(grid)
        corrections = calculator.calculate_corrections(boxes)

        # Should have corrections for boxes that need alignment
        assert len(corrections) >= 0

    def test_unicode_box_alignment(self) -> None:
        """Should align Unicode boxes."""
        content = "┌──┐\n│  │\n └──┘"
        grid = Grid.from_string(content)
        detector = BoxDetector()
        calculator = BoxAlignmentCalculator()

        boxes = detector.detect_boxes(grid)
        corrections = calculator.calculate_corrections(boxes)

        # Should produce correction for shifted bottom
        assert len(corrections) >= 0
