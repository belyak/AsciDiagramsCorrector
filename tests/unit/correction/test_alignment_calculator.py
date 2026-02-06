"""Unit tests for AlignmentCalculator."""

import pytest

from ascii_corrector.correction.alignment_calculator import AlignmentCalculator
from ascii_corrector.detection.protocols import ParallelGroup
from ascii_corrector.domain import Cell, Direction, Line


class TestAlignmentCalculatorHorizontal:
    """Tests for horizontal line alignment calculation."""

    def test_no_correction_needed_for_aligned_lines(self) -> None:
        """Should return no corrections for already aligned lines."""
        # Two lines at same row
        line1 = Line(
            cells=[Cell.from_value("-", row=5, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        line2 = Line(
            cells=[Cell.from_value("-", row=5, col=i + 10) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        group = ParallelGroup(
            lines=[line1, line2],
            direction=Direction.HORIZONTAL,
            reference_line=line1,
            expected_position=5,
        )

        calculator = AlignmentCalculator()
        result = calculator.calculate_alignment(group)

        # No corrections needed - lines already aligned
        assert len(result.corrections) == 0

    def test_calculate_correction_for_shifted_line(self) -> None:
        """Should calculate correction for shifted line."""
        # Reference at row 5, shifted at row 6
        reference = Line(
            cells=[Cell.from_value("-", row=5, col=i) for i in range(10)],
            direction=Direction.HORIZONTAL,
        )
        shifted = Line(
            cells=[Cell.from_value("-", row=6, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        group = ParallelGroup(
            lines=[reference, shifted],
            direction=Direction.HORIZONTAL,
            reference_line=reference,
            expected_position=5,
        )

        calculator = AlignmentCalculator()
        result = calculator.calculate_alignment(group)

        # Should have one correction for the shifted line
        assert len(result.corrections) == 1
        correction = result.corrections[0]
        assert correction.line == shifted
        assert correction.row_offset == -1  # Move up to align with reference

    def test_calculate_multiple_corrections(self) -> None:
        """Should calculate corrections for multiple shifted lines."""
        reference = Line(
            cells=[Cell.from_value("-", row=5, col=i) for i in range(10)],
            direction=Direction.HORIZONTAL,
        )
        shifted1 = Line(
            cells=[Cell.from_value("-", row=6, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        shifted2 = Line(
            cells=[Cell.from_value("-", row=4, col=i + 20) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        group = ParallelGroup(
            lines=[reference, shifted1, shifted2],
            direction=Direction.HORIZONTAL,
            reference_line=reference,
            expected_position=5,
        )

        calculator = AlignmentCalculator()
        result = calculator.calculate_alignment(group)

        assert len(result.corrections) == 2


class TestAlignmentCalculatorVertical:
    """Tests for vertical line alignment calculation."""

    def test_calculate_vertical_correction(self) -> None:
        """Should calculate column correction for vertical lines."""
        # Reference at col 5, shifted at col 6
        reference = Line(
            cells=[Cell.from_value("|", row=i, col=5) for i in range(10)],
            direction=Direction.VERTICAL,
        )
        shifted = Line(
            cells=[Cell.from_value("|", row=i, col=6) for i in range(5)],
            direction=Direction.VERTICAL,
        )
        group = ParallelGroup(
            lines=[reference, shifted],
            direction=Direction.VERTICAL,
            reference_line=reference,
            expected_position=5,
        )

        calculator = AlignmentCalculator()
        result = calculator.calculate_alignment(group)

        assert len(result.corrections) == 1
        correction = result.corrections[0]
        assert correction.col_offset == -1  # Move left to align


class TestAlignmentCalculatorEdgeCases:
    """Tests for edge cases."""

    def test_empty_group(self) -> None:
        """Should handle empty group."""
        group = ParallelGroup(
            lines=[],
            direction=Direction.HORIZONTAL,
        )

        calculator = AlignmentCalculator()
        result = calculator.calculate_alignment(group)

        assert len(result.corrections) == 0

    def test_single_line_group(self) -> None:
        """Should handle group with single line."""
        line = Line(
            cells=[Cell.from_value("-", row=5, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        group = ParallelGroup(
            lines=[line],
            direction=Direction.HORIZONTAL,
            reference_line=line,
            expected_position=5,
        )

        calculator = AlignmentCalculator()
        result = calculator.calculate_alignment(group)

        assert len(result.corrections) == 0
