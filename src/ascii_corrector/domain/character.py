"""Character value object for ASCII diagram characters."""

from __future__ import annotations

from dataclasses import dataclass

from ascii_corrector.domain.character_constants import (
    ARROW_CHARS,
    CORNER_CHARS,
    DIAGONAL_DOWN,
    DIAGONAL_UP,
    HORIZONTAL_CHARS,
    JUNCTION_CHARS,
    VERTICAL_CHARS,
    WHITESPACE_CHARS,
)
from ascii_corrector.domain.enums import CharacterClass


def _classify_character(value: str) -> CharacterClass:
    """
    Classify a single character into its CharacterClass.

    Args:
        value: Single character to classify.

    Returns:
        CharacterClass for the character.
    """
    if value in HORIZONTAL_CHARS:
        return CharacterClass.HORIZONTAL
    if value in VERTICAL_CHARS:
        return CharacterClass.VERTICAL
    if value in JUNCTION_CHARS:
        return CharacterClass.JUNCTION
    if value in CORNER_CHARS:
        return CharacterClass.CORNER
    if value in DIAGONAL_DOWN:
        return CharacterClass.DIAGONAL_DOWN
    if value in DIAGONAL_UP:
        return CharacterClass.DIAGONAL_UP
    if value in ARROW_CHARS:
        return CharacterClass.ARROW
    if value in WHITESPACE_CHARS:
        return CharacterClass.WHITESPACE
    if value.isalnum():
        return CharacterClass.TEXT
    return CharacterClass.UNKNOWN


@dataclass(frozen=True)
class Character:
    """
    Immutable character with classification.

    Represents a single ASCII character with methods to query its type
    for diagram processing purposes.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate character value."""
        if len(self.value) != 1:
            raise ValueError("Character must be exactly one character")

    @property
    def char_class(self) -> CharacterClass:
        """
        Classify the character type.

        Returns:
            CharacterClass indicating the type of this character.
        """
        return _classify_character(self.value)

    def is_line_char(self) -> bool:
        """
        Check if character is a line character (horizontal or vertical).

        Returns:
            True if character is used for drawing lines.
        """
        return self.char_class in (CharacterClass.HORIZONTAL, CharacterClass.VERTICAL)

    def is_corner(self) -> bool:
        """
        Check if character is a corner character.

        Returns:
            True if character is used for corners.
        """
        return self.char_class == CharacterClass.CORNER

    def is_junction(self) -> bool:
        """
        Check if character is a junction character.

        Returns:
            True if character is used for line junctions.
        """
        return self.char_class == CharacterClass.JUNCTION

    def is_whitespace(self) -> bool:
        """
        Check if character is whitespace.

        Returns:
            True if character is whitespace (space or tab).
        """
        return self.char_class == CharacterClass.WHITESPACE
