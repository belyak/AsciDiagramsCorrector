"""Unit tests for Position value object."""

import math

import pytest

from ascii_corrector.domain.position import Position


class TestPositionCreation:
    """Tests for Position creation and basic properties."""

    def test_create_position_with_row_and_col(self) -> None:
        """Position should store row and column."""
        pos = Position(row=5, col=10)

        assert pos.row == 5
        assert pos.col == 10

    def test_position_with_zero_coordinates(self) -> None:
        """Position should accept zero coordinates."""
        pos = Position(row=0, col=0)

        assert pos.row == 0
        assert pos.col == 0

    def test_position_with_negative_coordinates(self) -> None:
        """Position should accept negative coordinates."""
        pos = Position(row=-1, col=-5)

        assert pos.row == -1
        assert pos.col == -5


class TestPositionImmutability:
    """Tests for Position immutability."""

    def test_position_is_frozen(self) -> None:
        """Position should be immutable (frozen dataclass)."""
        pos = Position(row=0, col=0)

        with pytest.raises(AttributeError):
            pos.row = 1  # type: ignore[misc]

    def test_position_is_hashable(self) -> None:
        """Position should be hashable for use in sets/dicts."""
        pos = Position(row=1, col=2)

        # Should not raise
        hash(pos)
        {pos}  # noqa: B018
        {pos: "value"}  # noqa: B018


class TestPositionEquality:
    """Tests for Position equality comparison."""

    def test_equal_positions(self) -> None:
        """Positions with same coordinates should be equal."""
        pos1 = Position(row=5, col=10)
        pos2 = Position(row=5, col=10)

        assert pos1 == pos2

    def test_different_positions(self) -> None:
        """Positions with different coordinates should not be equal."""
        pos1 = Position(row=5, col=10)
        pos2 = Position(row=5, col=11)

        assert pos1 != pos2


class TestPositionOffset:
    """Tests for Position.offset() method."""

    def test_offset_returns_new_position(self) -> None:
        """Offset should return a new Position object."""
        pos = Position(row=5, col=5)
        new_pos = pos.offset(delta_row=-2, delta_col=3)

        assert new_pos is not pos
        assert isinstance(new_pos, Position)

    def test_offset_calculates_correctly(self) -> None:
        """Offset should correctly calculate new position."""
        pos = Position(row=5, col=5)
        new_pos = pos.offset(delta_row=-2, delta_col=3)

        assert new_pos.row == 3
        assert new_pos.col == 8

    def test_offset_preserves_original(self) -> None:
        """Offset should not modify the original position."""
        pos = Position(row=5, col=5)
        pos.offset(delta_row=-2, delta_col=3)

        assert pos.row == 5
        assert pos.col == 5

    def test_offset_with_zero(self) -> None:
        """Offset with zero deltas should return equal position."""
        pos = Position(row=5, col=5)
        new_pos = pos.offset(delta_row=0, delta_col=0)

        assert new_pos == pos


class TestPositionDistance:
    """Tests for Position.distance_to() method."""

    def test_distance_to_same_position(self) -> None:
        """Distance to same position should be zero."""
        pos = Position(row=5, col=5)

        assert pos.distance_to(pos) == 0.0

    def test_distance_to_horizontal(self) -> None:
        """Distance on horizontal line should be column difference."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=0, col=5)

        assert pos1.distance_to(pos2) == 5.0

    def test_distance_to_vertical(self) -> None:
        """Distance on vertical line should be row difference."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=3, col=0)

        assert pos1.distance_to(pos2) == 3.0

    def test_distance_to_diagonal(self) -> None:
        """Distance on diagonal should follow Pythagorean theorem."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=3, col=4)

        assert pos1.distance_to(pos2) == 5.0  # 3-4-5 triangle

    def test_distance_is_symmetric(self) -> None:
        """Distance should be symmetric."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=3, col=4)

        assert pos1.distance_to(pos2) == pos2.distance_to(pos1)


class TestPositionManhattanDistance:
    """Tests for Position.manhattan_distance_to() method."""

    def test_manhattan_distance_to_same_position(self) -> None:
        """Manhattan distance to same position should be zero."""
        pos = Position(row=5, col=5)

        assert pos.manhattan_distance_to(pos) == 0

    def test_manhattan_distance_horizontal(self) -> None:
        """Manhattan distance on horizontal should be column diff."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=0, col=5)

        assert pos1.manhattan_distance_to(pos2) == 5

    def test_manhattan_distance_vertical(self) -> None:
        """Manhattan distance on vertical should be row diff."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=3, col=0)

        assert pos1.manhattan_distance_to(pos2) == 3

    def test_manhattan_distance_diagonal(self) -> None:
        """Manhattan distance should sum row and column differences."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=3, col=4)

        assert pos1.manhattan_distance_to(pos2) == 7

    def test_manhattan_distance_is_symmetric(self) -> None:
        """Manhattan distance should be symmetric."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=3, col=4)

        assert pos1.manhattan_distance_to(pos2) == pos2.manhattan_distance_to(pos1)

    def test_manhattan_distance_returns_int(self) -> None:
        """Manhattan distance should return an integer."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=3, col=4)

        result = pos1.manhattan_distance_to(pos2)

        assert isinstance(result, int)
