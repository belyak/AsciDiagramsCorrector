"""Unit tests for domain enums."""

import pytest

from ascii_corrector.domain.enums import CharacterClass, Direction, LineType


class TestCharacterClass:
    """Tests for CharacterClass enum."""

    def test_character_class_has_horizontal(self) -> None:
        """CharacterClass should have HORIZONTAL variant."""
        assert CharacterClass.HORIZONTAL is not None

    def test_character_class_has_vertical(self) -> None:
        """CharacterClass should have VERTICAL variant."""
        assert CharacterClass.VERTICAL is not None

    def test_character_class_has_corner(self) -> None:
        """CharacterClass should have CORNER variant."""
        assert CharacterClass.CORNER is not None

    def test_character_class_has_junction(self) -> None:
        """CharacterClass should have JUNCTION variant."""
        assert CharacterClass.JUNCTION is not None

    def test_character_class_has_whitespace(self) -> None:
        """CharacterClass should have WHITESPACE variant."""
        assert CharacterClass.WHITESPACE is not None

    def test_character_class_values_are_unique(self) -> None:
        """All CharacterClass values should be unique."""
        values = [c.value for c in CharacterClass]
        assert len(values) == len(set(values))


class TestDirection:
    """Tests for Direction enum."""

    def test_direction_has_horizontal(self) -> None:
        """Direction should have HORIZONTAL variant."""
        assert Direction.HORIZONTAL is not None

    def test_direction_has_vertical(self) -> None:
        """Direction should have VERTICAL variant."""
        assert Direction.VERTICAL is not None

    def test_direction_values_are_unique(self) -> None:
        """All Direction values should be unique."""
        values = [d.value for d in Direction]
        assert len(values) == len(set(values))


class TestLineType:
    """Tests for LineType enum."""

    def test_line_type_has_horizontal(self) -> None:
        """LineType should have HORIZONTAL variant."""
        assert LineType.HORIZONTAL is not None

    def test_line_type_has_vertical(self) -> None:
        """LineType should have VERTICAL variant."""
        assert LineType.VERTICAL is not None

    def test_line_type_has_box_variants(self) -> None:
        """LineType should have BOX variants."""
        assert LineType.BOX_TOP is not None
        assert LineType.BOX_BOTTOM is not None
        assert LineType.BOX_LEFT is not None
        assert LineType.BOX_RIGHT is not None

    def test_line_type_values_are_unique(self) -> None:
        """All LineType values should be unique."""
        values = [lt.value for lt in LineType]
        assert len(values) == len(set(values))
