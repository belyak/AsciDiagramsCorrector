"""Unit tests for Cell entity."""

import pytest

from ascii_corrector.domain.cell import Cell
from ascii_corrector.domain.character import Character
from ascii_corrector.domain.position import Position


class TestCellCreation:
    """Tests for Cell creation."""

    def test_create_cell_with_character_and_position(self) -> None:
        """Cell should store character and position."""
        char = Character(value="-")
        pos = Position(row=5, col=10)

        cell = Cell(character=char, position=pos)

        assert cell.character == char
        assert cell.position == pos

    def test_cell_from_value(self) -> None:
        """Cell should be creatable from value and coordinates."""
        cell = Cell.from_value(value="-", row=5, col=10)

        assert cell.character.value == "-"
        assert cell.position.row == 5
        assert cell.position.col == 10


class TestCellImmutability:
    """Tests for Cell immutability."""

    def test_cell_is_frozen(self) -> None:
        """Cell should be immutable (frozen dataclass)."""
        cell = Cell.from_value(value="-", row=0, col=0)

        with pytest.raises(AttributeError):
            cell.position = Position(row=1, col=1)  # type: ignore[misc]


class TestCellIsEmpty:
    """Tests for Cell.is_empty() method."""

    def test_is_empty_for_space(self) -> None:
        """Space character should be considered empty."""
        cell = Cell.from_value(value=" ", row=0, col=0)

        assert cell.is_empty() is True

    def test_is_empty_for_tab(self) -> None:
        """Tab character should be considered empty."""
        cell = Cell.from_value(value="\t", row=0, col=0)

        assert cell.is_empty() is True

    @pytest.mark.parametrize("value", ["-", "|", "+", "a"])
    def test_is_empty_for_non_whitespace(self, value: str) -> None:
        """Non-whitespace characters should not be empty."""
        cell = Cell.from_value(value=value, row=0, col=0)

        assert cell.is_empty() is False


class TestCellIsStructural:
    """Tests for Cell.is_structural() method."""

    @pytest.mark.parametrize("value", ["-", "=", "_", "|", "!", "+", "*"])
    def test_is_structural_for_diagram_chars(self, value: str) -> None:
        """Diagram structural characters should return True."""
        cell = Cell.from_value(value=value, row=0, col=0)

        assert cell.is_structural() is True

    @pytest.mark.parametrize("value", [" ", "a", "Z", "@"])
    def test_is_structural_for_non_diagram_chars(self, value: str) -> None:
        """Non-structural characters should return False."""
        cell = Cell.from_value(value=value, row=0, col=0)

        assert cell.is_structural() is False


class TestCellNeighborPositions:
    """Tests for Cell.neighbor_positions() method."""

    def test_neighbor_positions_returns_four_positions(self) -> None:
        """Should return positions for up, down, left, right neighbors."""
        cell = Cell.from_value(value="-", row=5, col=5)

        neighbors = cell.neighbor_positions()

        assert len(neighbors) == 4

    def test_neighbor_positions_are_correct(self) -> None:
        """Neighbor positions should be adjacent cells."""
        cell = Cell.from_value(value="-", row=5, col=5)

        neighbors = cell.neighbor_positions()

        expected = {
            Position(row=4, col=5),  # up
            Position(row=6, col=5),  # down
            Position(row=5, col=4),  # left
            Position(row=5, col=6),  # right
        }
        assert set(neighbors) == expected

    def test_neighbor_positions_at_origin(self) -> None:
        """Neighbor positions at origin should include negative positions."""
        cell = Cell.from_value(value="-", row=0, col=0)

        neighbors = cell.neighbor_positions()

        # Some neighbors will have negative coordinates
        assert Position(row=-1, col=0) in neighbors
        assert Position(row=0, col=-1) in neighbors
