"""Cell entity combining Character and Position."""

from __future__ import annotations

from dataclasses import dataclass

from ascii_corrector.domain.character import Character
from ascii_corrector.domain.enums import CharacterClass
from ascii_corrector.domain.position import Position


@dataclass(frozen=True)
class Cell:
    """
    A cell in the ASCII diagram grid.

    Combines a Character with its Position in the grid.
    Provides methods for querying cell properties and relationships.
    """

    character: Character
    position: Position

    @classmethod
    def from_value(cls, value: str, row: int, col: int) -> Cell:
        """
        Create a Cell from a character value and coordinates.

        Args:
            value: Single character value.
            row: Row coordinate.
            col: Column coordinate.

        Returns:
            New Cell instance.
        """
        return cls(
            character=Character(value=value),
            position=Position(row=row, col=col),
        )

    def is_empty(self) -> bool:
        """
        Check if cell contains whitespace.

        Returns:
            True if cell contains space or tab.
        """
        return self.character.is_whitespace()

    def is_structural(self) -> bool:
        """
        Check if cell is part of diagram structure.

        Structural characters include lines, corners, and junctions.

        Returns:
            True if cell is a structural diagram element.
        """
        return self.character.char_class in (
            CharacterClass.HORIZONTAL,
            CharacterClass.VERTICAL,
            CharacterClass.CORNER,
            CharacterClass.JUNCTION,
        )

    def neighbor_positions(self) -> list[Position]:
        """
        Get positions of adjacent cells (up, down, left, right).

        Returns:
            List of four adjacent Position objects.
        """
        return [
            self.position.offset(delta_row=-1, delta_col=0),  # up
            self.position.offset(delta_row=1, delta_col=0),  # down
            self.position.offset(delta_row=0, delta_col=-1),  # left
            self.position.offset(delta_row=0, delta_col=1),  # right
        ]
