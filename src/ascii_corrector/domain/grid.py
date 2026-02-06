"""Grid aggregate for 2D character matrix."""

from __future__ import annotations

from ascii_corrector.domain.cell import Cell
from ascii_corrector.domain.character import Character
from ascii_corrector.domain.position import Position


class Grid:
    """
    2D character matrix representing an ASCII diagram.

    The Grid is the core data structure for diagram processing.
    It stores characters in a 2D array and provides methods for
    accessing and modifying cells.
    """

    def __init__(self, width: int = 0, height: int = 0) -> None:
        """
        Create a new Grid with given dimensions.

        Args:
            width: Number of columns.
            height: Number of rows.
        """
        self._width = width
        self._height = height
        # Initialize with spaces
        self._data: list[list[str]] = [
            [" " for _ in range(width)] for _ in range(height)
        ]

    @property
    def width(self) -> int:
        """Number of columns in the grid."""
        return self._width

    @property
    def height(self) -> int:
        """Number of rows in the grid."""
        return self._height

    @classmethod
    def from_string(cls, text: str) -> Grid:
        """
        Create a Grid from a multi-line string.

        Lines are split by newline characters. Shorter lines are
        padded with spaces to match the longest line.

        Args:
            text: Multi-line string representation of diagram.

        Returns:
            New Grid instance.
        """
        if not text:
            return cls(width=0, height=0)

        lines = text.split("\n")
        height = len(lines)
        width = max(len(line) for line in lines) if lines else 0

        grid = cls(width=width, height=height)

        for row_idx, line in enumerate(lines):
            for col_idx, char in enumerate(line):
                grid._data[row_idx][col_idx] = char

        return grid

    def to_string(self) -> str:
        """
        Convert grid to multi-line string representation.

        Trailing whitespace is stripped from each line.

        Returns:
            Multi-line string representation.
        """
        lines = []
        for row in self._data:
            line = "".join(row).rstrip()
            lines.append(line)

        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()

        return "\n".join(lines)

    def get_cell(self, position: Position) -> Cell | None:
        """
        Get cell at given position.

        Args:
            position: Grid position to query.

        Returns:
            Cell at position, or None if out of bounds.
        """
        if not self.is_valid_position(position):
            return None

        char_value = self._data[position.row][position.col]
        return Cell.from_value(value=char_value, row=position.row, col=position.col)

    def set_cell(self, position: Position, character: Character) -> None:
        """
        Set character at given position.

        Args:
            position: Grid position to modify.
            character: Character to place at position.

        Raises:
            IndexError: If position is out of bounds.
        """
        if not self.is_valid_position(position):
            raise IndexError(f"Position {position} is out of bounds")

        self._data[position.row][position.col] = character.value

    def clear_cell(self, position: Position) -> None:
        """
        Clear cell at given position (set to space).

        Args:
            position: Grid position to clear.

        Raises:
            IndexError: If position is out of bounds.
        """
        self.set_cell(position, Character(value=" "))

    def get_row(self, row: int) -> list[Cell]:
        """
        Get all cells in a row.

        Args:
            row: Row index.

        Returns:
            List of Cell objects in the row.

        Raises:
            IndexError: If row is out of bounds.
        """
        if row < 0 or row >= self._height:
            raise IndexError(f"Row {row} is out of bounds")

        return [
            Cell.from_value(value=self._data[row][col], row=row, col=col)
            for col in range(self._width)
        ]

    def get_col(self, col: int) -> list[Cell]:
        """
        Get all cells in a column.

        Args:
            col: Column index.

        Returns:
            List of Cell objects in the column.

        Raises:
            IndexError: If column is out of bounds.
        """
        if col < 0 or col >= self._width:
            raise IndexError(f"Column {col} is out of bounds")

        return [
            Cell.from_value(value=self._data[row][col], row=row, col=col)
            for row in range(self._height)
        ]

    def is_valid_position(self, position: Position) -> bool:
        """
        Check if position is within grid bounds.

        Args:
            position: Position to check.

        Returns:
            True if position is valid.
        """
        return 0 <= position.row < self._height and 0 <= position.col < self._width

    def copy(self) -> Grid:
        """
        Create a deep copy of the grid.

        Returns:
            New Grid with same content.
        """
        new_grid = Grid(width=self._width, height=self._height)
        for row in range(self._height):
            for col in range(self._width):
                new_grid._data[row][col] = self._data[row][col]
        return new_grid
