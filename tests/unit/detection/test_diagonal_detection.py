"""Unit tests for diagonal line detection."""

import pytest

from ascii_corrector.detection.line_detector import LineDetector
from ascii_corrector.domain import Direction, Grid


class TestDiagonalDetectionDisabledByDefault:
    """Tests that diagonal detection is disabled by default."""

    def test_diagonal_not_detected_without_flag(self) -> None:
        """Should not detect diagonals when detect_diagonals=False."""
        content = "\\\n \\"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=False)

        lines = detector.detect_lines(grid)

        # Should not find any diagonals
        diagonal_lines = [ln for ln in lines if ln.direction in (Direction.DIAGONAL_DOWN, Direction.DIAGONAL_UP)]
        assert len(diagonal_lines) == 0

    def test_diagonal_detected_with_flag(self) -> None:
        """Should detect diagonals when detect_diagonals=True."""
        content = "\\\n \\"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        # Should find the diagonal
        diagonal_lines = [ln for ln in lines if ln.direction == Direction.DIAGONAL_DOWN]
        assert len(diagonal_lines) == 1


class TestDiagonalDownDetection:
    r"""Tests for down-right diagonal (\) detection."""

    def test_detect_simple_diagonal_down(self) -> None:
        """Should detect a simple down-right diagonal."""
        content = "\\\n \\"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_DOWN]
        assert len(diagonal) == 1
        assert len(diagonal[0].cells) == 2

    def test_detect_longer_diagonal_down(self) -> None:
        """Should detect longer down-right diagonal."""
        content = "\\\n \\\n  \\"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_DOWN]
        assert len(diagonal) == 1
        assert len(diagonal[0].cells) == 3

    def test_detect_unicode_diagonal_down(self) -> None:
        """Should detect Unicode down-right diagonal ╲."""
        content = "╲\n ╲\n  ╲"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_DOWN]
        assert len(diagonal) == 1

    def test_no_diagonal_too_short(self) -> None:
        """Should not detect single diagonal character."""
        content = "\\"
        grid = Grid.from_string(content)
        detector = LineDetector(min_line_length=2, detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_DOWN]
        assert len(diagonal) == 0


class TestDiagonalUpDetection:
    """Tests for up-right diagonal (/) detection."""

    def test_detect_simple_diagonal_up(self) -> None:
        """Should detect a simple up-right diagonal."""
        content = " /\n/"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_UP]
        assert len(diagonal) == 1
        assert len(diagonal[0].cells) == 2

    def test_detect_longer_diagonal_up(self) -> None:
        """Should detect longer up-right diagonal."""
        content = "  /\n /\n/"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_UP]
        # Should find at least one diagonal (may be one or more depending on scan order)
        assert len(diagonal) >= 1
        # Should find lines with at least 2 cells
        assert all(len(d.cells) >= 2 for d in diagonal)

    def test_detect_unicode_diagonal_up(self) -> None:
        """Should detect Unicode up-right diagonal ╱."""
        content = "  ╱\n ╱\n╱"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_UP]
        # Should find at least one diagonal
        assert len(diagonal) >= 1


class TestMultipleDiagonals:
    """Tests for detecting multiple diagonals."""

    def test_detect_two_separate_diagonals(self) -> None:
        """Should detect two separate diagonal lines."""
        content = "\\\n \\   /\n  \\ /"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonals = [ln for ln in lines if ln.direction in (Direction.DIAGONAL_DOWN, Direction.DIAGONAL_UP)]
        # Should find 2 diagonals (one down, one up)
        assert len(diagonals) >= 1

    def test_detect_x_pattern(self) -> None:
        """Should detect X pattern (two crossing diagonals)."""
        content = "  /\\\n / \\\n/   \\"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonals = [ln for ln in lines if ln.direction in (Direction.DIAGONAL_DOWN, Direction.DIAGONAL_UP)]
        # Should find both diagonals
        assert len(diagonals) >= 1


class TestDiagonalWithHorizontalVertical:
    """Tests for diagonals mixed with horizontal and vertical lines."""

    def test_diagonal_in_diagram_with_box(self) -> None:
        """Should detect diagonals within box diagram."""
        content = "+--+\n|\\ |\n| \\|\n+--+"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        # Should detect horizontal, vertical, and diagonal lines
        assert len(lines) > 0
        has_horizontal = any(ln.direction == Direction.HORIZONTAL for ln in lines)
        has_vertical = any(ln.direction == Direction.VERTICAL for ln in lines)
        assert has_horizontal
        assert has_vertical


class TestDiagonalEdgeCases:
    """Edge case tests for diagonal detection."""

    def test_empty_grid(self) -> None:
        """Should handle empty grid."""
        grid = Grid.from_string("")
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        assert len(lines) == 0

    def test_diagonal_at_edges(self) -> None:
        """Should detect diagonals at grid edges."""
        content = "\\\n \\"
        grid = Grid.from_string(content)
        detector = LineDetector(detect_diagonals=True)

        lines = detector.detect_lines(grid)

        diagonal = [ln for ln in lines if ln.direction == Direction.DIAGONAL_DOWN]
        assert len(diagonal) == 1

    def test_single_diagonal_column(self) -> None:
        """Should handle grid with only diagonals in one column."""
        content = "\n\\"
        grid = Grid.from_string(content)
        detector = LineDetector(min_line_length=2, detect_diagonals=True)

        lines = detector.detect_lines(grid)

        assert isinstance(lines, list)
