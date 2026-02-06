"""Unit tests for Grid aggregate."""

import pytest

from ascii_corrector.domain.cell import Cell
from ascii_corrector.domain.character import Character
from ascii_corrector.domain.grid import Grid
from ascii_corrector.domain.position import Position


class TestGridCreation:
    """Tests for Grid creation."""

    def test_create_empty_grid(self) -> None:
        """Should create an empty grid with given dimensions."""
        grid = Grid(width=5, height=3)

        assert grid.width == 5
        assert grid.height == 3

    def test_from_string_simple_box(self) -> None:
        """Should parse a simple box from string."""
        text = "+--+\n|  |\n+--+"

        grid = Grid.from_string(text)

        assert grid.width == 4
        assert grid.height == 3

    def test_from_string_preserves_characters(self) -> None:
        """Characters should be preserved when parsing."""
        text = "+--+\n|  |\n+--+"

        grid = Grid.from_string(text)

        assert grid.get_cell(Position(row=0, col=0)).character.value == "+"
        assert grid.get_cell(Position(row=0, col=1)).character.value == "-"
        assert grid.get_cell(Position(row=1, col=0)).character.value == "|"
        assert grid.get_cell(Position(row=1, col=1)).character.value == " "

    def test_from_string_handles_varying_line_lengths(self) -> None:
        """Should handle lines of different lengths (pad with spaces)."""
        text = "+--+\n|\n+--+"

        grid = Grid.from_string(text)

        assert grid.width == 4  # Max line length
        # Short line should be padded
        assert grid.get_cell(Position(row=1, col=1)).character.value == " "

    def test_from_string_empty_string(self) -> None:
        """Empty string should create empty grid."""
        grid = Grid.from_string("")

        assert grid.width == 0
        assert grid.height == 0


class TestGridToString:
    """Tests for Grid.to_string() method."""

    def test_to_string_simple_box(self) -> None:
        """Should convert grid back to string."""
        original = "+--+\n|  |\n+--+"

        grid = Grid.from_string(original)
        result = grid.to_string()

        assert result == original

    def test_to_string_strips_trailing_whitespace(self) -> None:
        """Should strip trailing whitespace from lines."""
        grid = Grid.from_string("+--+\n|  |\n+--+")

        result = grid.to_string()

        lines = result.split("\n")
        for line in lines:
            assert line == line.rstrip()

    def test_round_trip_preserves_diagram(self) -> None:
        """Converting to string and back should preserve diagram."""
        original = "+----+\n| Hi |\n+----+"

        grid = Grid.from_string(original)
        result = Grid.from_string(grid.to_string())

        assert result.to_string() == original


class TestGridGetCell:
    """Tests for Grid.get_cell() method."""

    def test_get_cell_valid_position(self) -> None:
        """Should return cell at valid position."""
        grid = Grid.from_string("+--+\n|  |\n+--+")

        cell = grid.get_cell(Position(row=0, col=0))

        assert cell is not None
        assert cell.character.value == "+"
        assert cell.position == Position(row=0, col=0)

    def test_get_cell_out_of_bounds_returns_none(self) -> None:
        """Should return None for out-of-bounds position."""
        grid = Grid.from_string("+--+")

        assert grid.get_cell(Position(row=5, col=0)) is None
        assert grid.get_cell(Position(row=0, col=10)) is None
        assert grid.get_cell(Position(row=-1, col=0)) is None


class TestGridSetCell:
    """Tests for Grid.set_cell() method."""

    def test_set_cell_updates_grid(self) -> None:
        """Should update character at position."""
        grid = Grid.from_string("+--+\n|  |\n+--+")

        grid.set_cell(Position(row=1, col=1), Character(value="X"))

        assert grid.get_cell(Position(row=1, col=1)).character.value == "X"

    def test_set_cell_out_of_bounds_raises(self) -> None:
        """Should raise error for out-of-bounds position."""
        grid = Grid.from_string("+--+")

        with pytest.raises(IndexError):
            grid.set_cell(Position(row=5, col=0), Character(value="X"))


class TestGridClearCell:
    """Tests for Grid.clear_cell() method."""

    def test_clear_cell_sets_to_space(self) -> None:
        """Should set cell to space character."""
        grid = Grid.from_string("+--+")

        grid.clear_cell(Position(row=0, col=1))

        assert grid.get_cell(Position(row=0, col=1)).character.value == " "


class TestGridGetRow:
    """Tests for Grid.get_row() method."""

    def test_get_row_returns_cells(self) -> None:
        """Should return all cells in a row."""
        grid = Grid.from_string("+--+\n|  |\n+--+")

        row = grid.get_row(0)

        assert len(row) == 4
        assert row[0].character.value == "+"
        assert row[1].character.value == "-"

    def test_get_row_out_of_bounds_raises(self) -> None:
        """Should raise error for invalid row."""
        grid = Grid.from_string("+--+")

        with pytest.raises(IndexError):
            grid.get_row(5)


class TestGridGetCol:
    """Tests for Grid.get_col() method."""

    def test_get_col_returns_cells(self) -> None:
        """Should return all cells in a column."""
        grid = Grid.from_string("+--+\n|  |\n+--+")

        col = grid.get_col(0)

        assert len(col) == 3
        assert col[0].character.value == "+"
        assert col[1].character.value == "|"
        assert col[2].character.value == "+"

    def test_get_col_out_of_bounds_raises(self) -> None:
        """Should raise error for invalid column."""
        grid = Grid.from_string("+--+")

        with pytest.raises(IndexError):
            grid.get_col(10)


class TestGridIsValidPosition:
    """Tests for Grid.is_valid_position() method."""

    def test_valid_position_returns_true(self) -> None:
        """Should return True for valid positions."""
        grid = Grid.from_string("+--+\n|  |\n+--+")

        assert grid.is_valid_position(Position(row=0, col=0)) is True
        assert grid.is_valid_position(Position(row=2, col=3)) is True

    def test_invalid_position_returns_false(self) -> None:
        """Should return False for invalid positions."""
        grid = Grid.from_string("+--+\n|  |\n+--+")

        assert grid.is_valid_position(Position(row=-1, col=0)) is False
        assert grid.is_valid_position(Position(row=0, col=-1)) is False
        assert grid.is_valid_position(Position(row=5, col=0)) is False
        assert grid.is_valid_position(Position(row=0, col=10)) is False


class TestGridCopy:
    """Tests for Grid.copy() method."""

    def test_copy_creates_new_grid(self) -> None:
        """Should create a new independent grid."""
        grid = Grid.from_string("+--+")

        copy = grid.copy()

        assert copy is not grid
        assert copy.to_string() == grid.to_string()

    def test_copy_is_independent(self) -> None:
        """Modifying copy should not affect original."""
        grid = Grid.from_string("+--+")
        copy = grid.copy()

        copy.set_cell(Position(row=0, col=1), Character(value="X"))

        assert grid.get_cell(Position(row=0, col=1)).character.value == "-"
        assert copy.get_cell(Position(row=0, col=1)).character.value == "X"
