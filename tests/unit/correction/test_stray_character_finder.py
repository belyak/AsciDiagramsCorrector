"""Unit tests for StrayCharacterFinder."""

import pytest

from ascii_corrector.correction.stray_character_finder import StrayCharacterFinder
from ascii_corrector.detection.line_detector import LineDetector
from ascii_corrector.domain import Cell, Character, Direction, Grid, Line, Position


class TestStrayCharacterFinderVertical:
    """Tests for stray vertical character detection."""

    def test_find_stray_pipe_shifted_right(self) -> None:
        """Stray | shifted right of a detected vertical line should produce correction."""
        # Vertical line at col 0, stray | at col 1 on row 2
        grid = Grid.from_string(
            "|\n"
            "|\n"
            " |\n"
            "|\n"
            "|"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1
        assert corrections[0].row_offset == 0

    def test_find_stray_pipe_shifted_left(self) -> None:
        """Stray | shifted left of a detected vertical line should produce correction."""
        # Vertical line at col 1, stray | at col 0 on row 2
        grid = Grid.from_string(
            " |\n"
            " |\n"
            "|\n"
            " |\n"
            " |"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 1
        assert corrections[0].col_offset == 1
        assert corrections[0].row_offset == 0

    def test_no_correction_when_target_occupied(self) -> None:
        """No correction when the target position already has a non-space char."""
        # Vertical line at col 0, stray | at col 1 on row 2, but col 0 row 2 has 'x'
        grid = Grid.from_string(
            "|\n"
            "|\n"
            "x|\n"
            "|\n"
            "|"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 0

    def test_no_correction_when_stray_outside_line_range(self) -> None:
        """No correction when stray row is outside the line's row span + tolerance."""
        # Vertical line at col 0 rows 0-1, stray | at col 1 row 5 (outside range)
        grid = Grid.from_string(
            "|\n"
            "|\n"
            " \n"
            " \n"
            " \n"
            " |"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 0

    def test_no_correction_beyond_tolerance(self) -> None:
        """No correction when stray is more than tolerance columns from nearest line."""
        # Vertical line at col 0, stray | at col 3 (distance 3, beyond tolerance=1)
        grid = Grid.from_string(
            "|  \n"
            "|  \n"
            "   |\n"
            "|  \n"
            "|  "
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 0


class TestStrayCharacterFinderHorizontal:
    """Tests for stray horizontal character detection."""

    def test_find_stray_dash_shifted_down(self) -> None:
        """Stray - shifted down from a detected horizontal line should produce correction."""
        # Line on row 0 at cols 0-4, stray - at row 1 col 5 (within col range + tolerance)
        # Target position (row=0, col=5) is a space
        grid = Grid.from_string(
            "-----  \n"
            "     - "
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 1
        assert corrections[0].row_offset == -1
        assert corrections[0].col_offset == 0


class TestStrayCharacterFinderEdgeCases:
    """Edge case tests for StrayCharacterFinder."""

    def test_no_strays_when_all_chars_detected(self) -> None:
        """No corrections when all line chars are part of detected lines."""
        grid = Grid.from_string(
            "|\n"
            "|\n"
            "|"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 0

    def test_stray_near_multiple_lines_picks_closest(self) -> None:
        """Stray between two lines should be corrected toward the closest one."""
        # Line at col 0, line at col 4, stray at col 1 (closer to col 0)
        grid = Grid.from_string(
            "|   |\n"
            "|   |\n"
            " |  |\n"
            "|   |\n"
            "|   |"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 1
        # Should move to col 0 (distance 1), not col 4 (distance 3)
        assert corrections[0].col_offset == -1

    def test_no_correction_when_text_between_pipes(self) -> None:
        """No correction when there is text between the stray and the next pipe."""
        # Stray | at col 2 has text "AB" between it and | at col 5
        # Moving the | would compress the text spacing
        grid = Grid.from_string(
            "|    |\n"
            "|    |\n"
            " | AB|\n"
            "|    |\n"
            "|    |"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 0

    def test_correction_for_right_edge_pipe_with_text(self) -> None:
        """Correction IS produced for the rightmost pipe even on rows with text."""
        # Right-edge | at col 6 instead of 5, text on row
        grid = Grid.from_string(
            "|    |\n"
            "| AB |\n"
            "| CD  |\n"  # right | shifted right by 1
            "| EF |\n"
            "|    |"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        # The right-edge | at col 6 should be corrected to col 5
        right_edge_corrs = [c for c in corrections if c.col_offset == -1]
        assert len(right_edge_corrs) == 1

    def test_correction_when_only_whitespace_between_pipes(self) -> None:
        """Correction IS produced when only whitespace between stray and next pipe."""
        # Row 2 has stray | at col 2, only whitespace between it and next | at col 5
        grid = Grid.from_string(
            "|    |\n"
            "|    |\n"
            " |   |\n"
            "|    |\n"
            "|    |"
        )
        detector = LineDetector(min_line_length=2)
        lines = detector.detect_lines(grid)

        finder = StrayCharacterFinder(tolerance=1)
        corrections = finder.find_stray_corrections(grid, lines)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1
