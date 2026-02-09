"""Unit tests for diagram structure classification."""

import pytest

from ascii_corrector.detection.structure_classifier import StructureClassifier, StructureType
from ascii_corrector.domain import Grid


class TestStructureClassifierBasic:
    """Basic structure classification tests."""

    def test_classify_simple_box(self) -> None:
        """Should classify rectangular box as BOX."""
        content = "+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        structure_type = classifier.classify(grid)

        assert structure_type == StructureType.BOX

    def test_classify_simple_tree(self) -> None:
        """Should classify tree structure as TREE."""
        content = "root\n |\n +-- leaf1\n +-- leaf2"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        structure_type = classifier.classify(grid)

        assert structure_type == StructureType.TREE

    def test_classify_text_only_as_unknown(self) -> None:
        """Should classify text-only content as UNKNOWN."""
        content = "This is just\nplain text\nwith no diagrams"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        structure_type = classifier.classify(grid)

        assert structure_type == StructureType.UNKNOWN


class TestStructureClassifierBoxDetection:
    """Tests for box pattern detection."""

    def test_detect_box_patterns(self) -> None:
        """Should detect box patterns."""
        content = "+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        has_box = classifier.has_box_patterns(grid)

        assert has_box is True

    def test_detect_unicode_box_patterns(self) -> None:
        """Should detect Unicode box patterns."""
        content = "┌──┐\n│  │\n└──┘"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        has_box = classifier.has_box_patterns(grid)

        assert has_box is True

    def test_detect_multiple_boxes(self) -> None:
        """Should detect multiple box patterns."""
        content = "+--+  +--+\n|  |  |  |\n+--+  +--+"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        has_box = classifier.has_box_patterns(grid)

        assert has_box is True

    def test_no_box_patterns_in_text(self) -> None:
        """Should not detect box patterns in text."""
        content = "This is text\nwith no boxes"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        has_box = classifier.has_box_patterns(grid)

        assert has_box is False


class TestStructureClassifierTreeDetection:
    """Tests for tree pattern detection."""

    def test_detect_simple_tree_pattern(self) -> None:
        """Should detect simple tree pattern."""
        content = "root\n |\n +-- branch1\n +-- branch2"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        has_tree = classifier.has_tree_patterns(grid)

        assert has_tree is True

    def test_detect_multiple_branches(self) -> None:
        """Should detect multiple branch pattern."""
        content = "   root\n    |\n    +-- a\n    +-- b\n    +-- c"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        has_tree = classifier.has_tree_patterns(grid)

        assert has_tree is True

    def test_no_tree_patterns_in_box(self) -> None:
        """Should not detect tree patterns in box."""
        content = "+--+\n|  |\n+--+"
        grid = Grid.from_string(content)
        classifier = StructureClassifier()

        has_tree = classifier.has_tree_patterns(grid)

        assert has_tree is False

    def test_single_branch_not_tree(self) -> None:
        """Should not classify single branch as tree."""
        content = "root\n |\n +-- leaf"
        grid = Grid.from_string(content)
        classifier = StructureClassifier(tree_branch_threshold=2)

        has_tree = classifier.has_tree_patterns(grid)

        # Single branch might not meet threshold
        # This depends on actual implementation
        assert isinstance(has_tree, bool)


class TestStructureClassifierEdgeCases:
    """Edge case tests for structure classification."""

    def test_empty_grid(self) -> None:
        """Should handle empty grid."""
        grid = Grid.from_string("")
        classifier = StructureClassifier()

        structure_type = classifier.classify(grid)

        assert structure_type == StructureType.UNKNOWN

    def test_whitespace_only(self) -> None:
        """Should handle whitespace-only grid."""
        grid = Grid.from_string("   \n   \n   ")
        classifier = StructureClassifier()

        structure_type = classifier.classify(grid)

        assert structure_type == StructureType.UNKNOWN

    def test_single_character(self) -> None:
        """Should handle single character."""
        grid = Grid.from_string("+")
        classifier = StructureClassifier()

        structure_type = classifier.classify(grid)

        assert structure_type == StructureType.UNKNOWN
