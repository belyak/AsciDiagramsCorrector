"""Unit tests for ShiftCorrector."""

import pytest

from ascii_corrector.correction.protocols import ShiftCorrection
from ascii_corrector.correction.shift_corrector import ShiftCorrector
from ascii_corrector.domain import Cell, Direction, Grid, Line, Position


class TestShiftCorrectorHorizontal:
    """Tests for horizontal line shift correction."""

    def test_shift_line_up(self) -> None:
        """Should shift a horizontal line up."""
        grid = Grid.from_string("     \n-----\n     ")
        line = Line(
            cells=[Cell.from_value("-", row=1, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        correction = ShiftCorrection(line=line, row_offset=-1, col_offset=0)

        corrector = ShiftCorrector()
        result = corrector.apply_correction(correction, grid)

        # Line should now be at row 0
        assert result.get_cell(Position(row=0, col=0)).character.value == "-"
        assert result.get_cell(Position(row=0, col=4)).character.value == "-"
        # Original position should be cleared
        assert result.get_cell(Position(row=1, col=0)).character.value == " "

    def test_shift_line_down(self) -> None:
        """Should shift a horizontal line down."""
        grid = Grid.from_string("-----\n     \n     ")
        line = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        correction = ShiftCorrection(line=line, row_offset=1, col_offset=0)

        corrector = ShiftCorrector()
        result = corrector.apply_correction(correction, grid)

        # Line should now be at row 1
        assert result.get_cell(Position(row=1, col=0)).character.value == "-"
        # Original position should be cleared
        assert result.get_cell(Position(row=0, col=0)).character.value == " "


class TestShiftCorrectorVertical:
    """Tests for vertical line shift correction."""

    def test_shift_line_left(self) -> None:
        """Should shift a vertical line left."""
        grid = Grid.from_string(" | \n | \n | ")
        line = Line(
            cells=[Cell.from_value("|", row=i, col=1) for i in range(3)],
            direction=Direction.VERTICAL,
        )
        correction = ShiftCorrection(line=line, row_offset=0, col_offset=-1)

        corrector = ShiftCorrector()
        result = corrector.apply_correction(correction, grid)

        # Line should now be at col 0
        assert result.get_cell(Position(row=0, col=0)).character.value == "|"
        assert result.get_cell(Position(row=2, col=0)).character.value == "|"
        # Original position should be cleared
        assert result.get_cell(Position(row=0, col=1)).character.value == " "

    def test_shift_line_right(self) -> None:
        """Should shift a vertical line right."""
        grid = Grid.from_string("|  \n|  \n|  ")
        line = Line(
            cells=[Cell.from_value("|", row=i, col=0) for i in range(3)],
            direction=Direction.VERTICAL,
        )
        correction = ShiftCorrection(line=line, row_offset=0, col_offset=1)

        corrector = ShiftCorrector()
        result = corrector.apply_correction(correction, grid)

        # Line should now be at col 1
        assert result.get_cell(Position(row=0, col=1)).character.value == "|"
        # Original position should be cleared
        assert result.get_cell(Position(row=0, col=0)).character.value == " "


class TestShiftCorrectorPreservation:
    """Tests for grid preservation during correction."""

    def test_preserves_other_content(self) -> None:
        """Should preserve content not part of the shifted line."""
        grid = Grid.from_string("+--+\n|--|\n+--+")
        # Shift the middle dashes (row 1)
        line = Line(
            cells=[Cell.from_value("-", row=1, col=i) for i in range(1, 3)],
            direction=Direction.HORIZONTAL,
        )
        # Note: In practice we wouldn't do this, but testing preservation
        correction = ShiftCorrection(line=line, row_offset=0, col_offset=0)

        corrector = ShiftCorrector()
        result = corrector.apply_correction(correction, grid)

        # Corners should be preserved
        assert result.get_cell(Position(row=0, col=0)).character.value == "+"
        assert result.get_cell(Position(row=2, col=3)).character.value == "+"

    def test_does_not_modify_original_grid(self) -> None:
        """Should not modify the original grid."""
        grid = Grid.from_string("-----\n     ")
        original_string = grid.to_string()
        line = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        correction = ShiftCorrection(line=line, row_offset=1, col_offset=0)

        corrector = ShiftCorrector()
        corrector.apply_correction(correction, grid)

        # Original should be unchanged
        assert grid.to_string() == original_string


class TestShiftCorrectorValidation:
    """Tests for correction validation."""

    def test_reject_out_of_bounds_shift(self) -> None:
        """Should reject shifts that would go out of bounds."""
        grid = Grid.from_string("-----")
        line = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        # Shift up from row 0 would go to row -1
        correction = ShiftCorrection(line=line, row_offset=-1, col_offset=0)

        corrector = ShiftCorrector()

        with pytest.raises(ValueError, match="out of bounds"):
            corrector.apply_correction(correction, grid)

    def test_zero_offset_returns_copy(self) -> None:
        """Zero offset should return a copy without changes."""
        grid = Grid.from_string("-----")
        line = Line(
            cells=[Cell.from_value("-", row=0, col=i) for i in range(5)],
            direction=Direction.HORIZONTAL,
        )
        correction = ShiftCorrection(line=line, row_offset=0, col_offset=0)

        corrector = ShiftCorrector()
        result = corrector.apply_correction(correction, grid)

        assert result.to_string() == grid.to_string()
        assert result is not grid  # Should be a copy
