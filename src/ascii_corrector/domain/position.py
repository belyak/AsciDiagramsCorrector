"""Position value object for 2D grid coordinates."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """
    Immutable 2D coordinate in the grid.

    Represents a position with row and column coordinates.
    Frozen dataclass ensures immutability and hashability.
    """

    row: int
    col: int

    def offset(self, delta_row: int, delta_col: int) -> Position:
        """
        Return new position offset by given deltas.

        Args:
            delta_row: Row offset (positive = down, negative = up)
            delta_col: Column offset (positive = right, negative = left)

        Returns:
            New Position with adjusted coordinates.
        """
        return Position(row=self.row + delta_row, col=self.col + delta_col)

    def distance_to(self, other: Position) -> float:
        """
        Calculate Euclidean distance to another position.

        Args:
            other: Target position.

        Returns:
            Euclidean distance as float.
        """
        return math.sqrt((self.row - other.row) ** 2 + (self.col - other.col) ** 2)

    def manhattan_distance_to(self, other: Position) -> int:
        """
        Calculate Manhattan distance to another position.

        Manhattan distance is the sum of absolute differences
        in row and column coordinates.

        Args:
            other: Target position.

        Returns:
            Manhattan distance as integer.
        """
        return abs(self.row - other.row) + abs(self.col - other.col)
