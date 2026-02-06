"""Character value object for ASCII diagram characters."""

from __future__ import annotations

from dataclasses import dataclass

from ascii_corrector.domain.enums import CharacterClass

# Character classification sets
_HORIZONTAL_CHARS: frozenset[str] = frozenset({"-", "=", "_"})
_VERTICAL_CHARS: frozenset[str] = frozenset({"|", "!"})
_CORNER_CHARS: frozenset[str] = frozenset({"+", ".", "'", "`"})
_JUNCTION_CHARS: frozenset[str] = frozenset({"*"})
_ARROW_CHARS: frozenset[str] = frozenset({"<", ">", "^", "v", "V"})
_WHITESPACE_CHARS: frozenset[str] = frozenset({" ", "\t"})


def _classify_character(value: str) -> CharacterClass:
    """
    Classify a single character into its CharacterClass.

    Args:
        value: Single character to classify.

    Returns:
        CharacterClass for the character.
    """
    if value in _HORIZONTAL_CHARS:
        return CharacterClass.HORIZONTAL
    if value in _VERTICAL_CHARS:
        return CharacterClass.VERTICAL
    if value in _CORNER_CHARS:
        return CharacterClass.CORNER
    if value in _JUNCTION_CHARS:
        return CharacterClass.JUNCTION
    if value in _ARROW_CHARS:
        return CharacterClass.ARROW
    if value in _WHITESPACE_CHARS:
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
