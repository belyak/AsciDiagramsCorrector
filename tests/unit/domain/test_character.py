"""Unit tests for Character value object."""

import pytest

from ascii_corrector.domain.character import Character
from ascii_corrector.domain.enums import CharacterClass


class TestCharacterCreation:
    """Tests for Character creation."""

    def test_create_character_with_value(self) -> None:
        """Character should store its value."""
        char = Character(value="-")

        assert char.value == "-"

    def test_character_must_be_single_char(self) -> None:
        """Character value must be exactly one character."""
        with pytest.raises(ValueError, match="exactly one character"):
            Character(value="--")

    def test_character_cannot_be_empty(self) -> None:
        """Character value cannot be empty string."""
        with pytest.raises(ValueError, match="exactly one character"):
            Character(value="")


class TestCharacterImmutability:
    """Tests for Character immutability."""

    def test_character_is_frozen(self) -> None:
        """Character should be immutable (frozen dataclass)."""
        char = Character(value="-")

        with pytest.raises(AttributeError):
            char.value = "="  # type: ignore[misc]

    def test_character_is_hashable(self) -> None:
        """Character should be hashable."""
        char = Character(value="-")

        # Should not raise
        hash(char)
        {char}  # noqa: B018


class TestCharacterClassification:
    """Tests for Character.char_class property."""

    @pytest.mark.parametrize("value", ["-", "=", "_"])
    def test_horizontal_characters(self, value: str) -> None:
        """Horizontal line characters should be classified as HORIZONTAL."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.HORIZONTAL

    @pytest.mark.parametrize("value", ["|", "!"])
    def test_vertical_characters(self, value: str) -> None:
        """Vertical line characters should be classified as VERTICAL."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.VERTICAL

    @pytest.mark.parametrize("value", ["+", ".", "'", "`"])
    def test_corner_characters(self, value: str) -> None:
        """Corner characters should be classified as CORNER."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.CORNER

    @pytest.mark.parametrize("value", ["*"])
    def test_junction_characters(self, value: str) -> None:
        """Junction characters should be classified as JUNCTION."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.JUNCTION

    @pytest.mark.parametrize("value", ["<", ">", "^", "v", "V"])
    def test_arrow_characters(self, value: str) -> None:
        """Arrow characters should be classified as ARROW."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.ARROW

    @pytest.mark.parametrize("value", [" ", "\t"])
    def test_whitespace_characters(self, value: str) -> None:
        """Whitespace characters should be classified as WHITESPACE."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.WHITESPACE

    @pytest.mark.parametrize("value", ["a", "Z", "5"])
    def test_text_characters(self, value: str) -> None:
        """Alphanumeric characters should be classified as TEXT."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.TEXT

    def test_unknown_characters(self) -> None:
        """Unknown characters should be classified as UNKNOWN."""
        char = Character(value="@")

        assert char.char_class == CharacterClass.UNKNOWN


class TestCharacterLineChecks:
    """Tests for Character.is_line_char() method."""

    @pytest.mark.parametrize("value", ["-", "=", "_", "|", "!"])
    def test_is_line_char_returns_true_for_lines(self, value: str) -> None:
        """is_line_char should return True for line characters."""
        char = Character(value=value)

        assert char.is_line_char() is True

    @pytest.mark.parametrize("value", ["+", " ", "a", "*"])
    def test_is_line_char_returns_false_for_non_lines(self, value: str) -> None:
        """is_line_char should return False for non-line characters."""
        char = Character(value=value)

        assert char.is_line_char() is False


class TestCharacterCornerChecks:
    """Tests for Character.is_corner() method."""

    @pytest.mark.parametrize("value", ["+", ".", "'", "`"])
    def test_is_corner_returns_true_for_corners(self, value: str) -> None:
        """is_corner should return True for corner characters."""
        char = Character(value=value)

        assert char.is_corner() is True

    @pytest.mark.parametrize("value", ["-", "|", " ", "a"])
    def test_is_corner_returns_false_for_non_corners(self, value: str) -> None:
        """is_corner should return False for non-corner characters."""
        char = Character(value=value)

        assert char.is_corner() is False


class TestCharacterJunctionChecks:
    """Tests for Character.is_junction() method."""

    @pytest.mark.parametrize("value", ["*"])
    def test_is_junction_returns_true_for_junctions(self, value: str) -> None:
        """is_junction should return True for junction characters."""
        char = Character(value=value)

        assert char.is_junction() is True

    @pytest.mark.parametrize("value", ["-", "|", "+", " "])
    def test_is_junction_returns_false_for_non_junctions(self, value: str) -> None:
        """is_junction should return False for non-junction characters."""
        char = Character(value=value)

        assert char.is_junction() is False


class TestCharacterWhitespaceChecks:
    """Tests for Character.is_whitespace() method."""

    @pytest.mark.parametrize("value", [" ", "\t"])
    def test_is_whitespace_returns_true_for_whitespace(self, value: str) -> None:
        """is_whitespace should return True for whitespace characters."""
        char = Character(value=value)

        assert char.is_whitespace() is True

    @pytest.mark.parametrize("value", ["-", "|", "+", "a"])
    def test_is_whitespace_returns_false_for_non_whitespace(self, value: str) -> None:
        """is_whitespace should return False for non-whitespace characters."""
        char = Character(value=value)

        assert char.is_whitespace() is False


class TestUnicodeHorizontalCharacters:
    """Tests for Unicode horizontal line character classification."""

    @pytest.mark.parametrize("value", ["─", "━", "═"])
    def test_unicode_horizontal_characters_classified_as_horizontal(self, value: str) -> None:
        """Unicode horizontal characters should be classified as HORIZONTAL."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.HORIZONTAL

    @pytest.mark.parametrize("value", ["─", "━", "═"])
    def test_unicode_horizontal_is_line_char(self, value: str) -> None:
        """Unicode horizontal characters should be recognized as line chars."""
        char = Character(value=value)

        assert char.is_line_char() is True


class TestUnicodeVerticalCharacters:
    """Tests for Unicode vertical line character classification."""

    @pytest.mark.parametrize("value", ["│", "┃", "║"])
    def test_unicode_vertical_characters_classified_as_vertical(self, value: str) -> None:
        """Unicode vertical characters should be classified as VERTICAL."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.VERTICAL

    @pytest.mark.parametrize("value", ["│", "┃", "║"])
    def test_unicode_vertical_is_line_char(self, value: str) -> None:
        """Unicode vertical characters should be recognized as line chars."""
        char = Character(value=value)

        assert char.is_line_char() is True


class TestUnicodeCornerCharacters:
    """Tests for Unicode corner character classification."""

    @pytest.mark.parametrize(
        "value",
        [
            "┌",
            "┐",
            "└",
            "┘",
            "╔",
            "╗",
            "╚",
            "╝",
            "┏",
            "┓",
            "┗",
            "┛",
        ],
    )
    def test_unicode_corner_characters_classified_as_corner(self, value: str) -> None:
        """Unicode corner characters should be classified as CORNER."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.CORNER

    @pytest.mark.parametrize("value", ["┌", "┐", "└", "┘"])
    def test_unicode_corner_is_corner(self, value: str) -> None:
        """Unicode corner characters should be recognized as corners."""
        char = Character(value=value)

        assert char.is_corner() is True


class TestUnicodeJunctionCharacters:
    """Tests for Unicode junction character classification."""

    @pytest.mark.parametrize("value", ["┼", "├", "┤", "┬", "┴"])
    def test_unicode_junction_characters_classified_as_junction(self, value: str) -> None:
        """Unicode junction characters should be classified as JUNCTION."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.JUNCTION

    @pytest.mark.parametrize("value", ["┼", "├", "┤", "┬", "┴"])
    def test_unicode_junction_is_junction(self, value: str) -> None:
        """Unicode junction characters should be recognized as junctions."""
        char = Character(value=value)

        assert char.is_junction() is True


class TestDiagonalCharacters:
    """Tests for diagonal line character classification."""

    @pytest.mark.parametrize("value", ["\\", "╲"])
    def test_diagonal_down_characters_classified_as_diagonal_down(self, value: str) -> None:
        """Diagonal down characters should be classified as DIAGONAL_DOWN."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.DIAGONAL_DOWN

    @pytest.mark.parametrize("value", ["/", "╱"])
    def test_diagonal_up_characters_classified_as_diagonal_up(self, value: str) -> None:
        """Diagonal up characters should be classified as DIAGONAL_UP."""
        char = Character(value=value)

        assert char.char_class == CharacterClass.DIAGONAL_UP
