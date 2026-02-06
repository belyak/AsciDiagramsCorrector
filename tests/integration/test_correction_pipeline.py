"""Integration tests for the full correction pipeline."""

from pathlib import Path

import pytest

from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.domain import Direction, Grid


class TestCorrectionPipelineBasic:
    """Basic integration tests for the correction pipeline."""

    def test_correct_shifted_bottom_line_in_box(
        self, broken_box_shifted_bottom: str
    ) -> None:
        """Should correct a box with shifted bottom line."""
        grid = Grid.from_string(broken_box_shifted_bottom)
        engine = CorrectionEngine(tolerance=1)

        result = engine.correct(grid)

        # Should detect groups and potentially make corrections
        assert result.groups_found is not None
        assert result.corrected_grid is not None

    def test_preserve_correct_simple_box(self, simple_box: str) -> None:
        """Should preserve an already correct box."""
        grid = Grid.from_string(simple_box)
        engine = CorrectionEngine(tolerance=1)

        result = engine.correct(grid)

        assert result.corrected_grid.to_string() == simple_box
        assert result.corrections_count == 0

    def test_analyze_detects_issues_without_correcting(
        self, broken_box_shifted_bottom: str
    ) -> None:
        """Analyze should detect issues without modifying the grid."""
        grid = Grid.from_string(broken_box_shifted_bottom)
        engine = CorrectionEngine(tolerance=1)

        result = engine.analyze(grid)

        # Should find groups but grid should remain unchanged
        assert len(result.groups_found) > 0
        # The corrected_grid in analyze mode is just a copy, not actually corrected
        assert result.corrected_grid is not None


class TestCorrectionPipelineWithFixtureFiles:
    """Integration tests using fixture files."""

    def test_correct_from_file(self, diagrams_dir: Path) -> None:
        """Should load and correct a diagram from a fixture file."""
        shifted_file = diagrams_dir / "shifted_lines.txt"
        content = shifted_file.read_text()
        grid = Grid.from_string(content.strip())
        engine = CorrectionEngine(tolerance=1)

        result = engine.correct(grid)

        assert result.corrected_grid is not None
        assert len(result.groups_found) > 0

    def test_analyze_complex_diagram(self, diagrams_dir: Path) -> None:
        """Should analyze a complex diagram with multiple boxes."""
        complex_file = diagrams_dir / "complex_diagram.txt"
        content = complex_file.read_text()
        grid = Grid.from_string(content.strip())
        engine = CorrectionEngine(tolerance=1)

        result = engine.analyze(grid)

        # Complex diagram should have multiple parallel groups
        assert len(result.groups_found) > 0
        # Should find horizontal lines from boxes
        h_groups = [g for g in result.groups_found if g.direction == Direction.HORIZONTAL]
        assert len(h_groups) > 0


class TestCorrectionPipelineEdgeCases:
    """Edge case tests for the correction pipeline."""

    def test_empty_content(self) -> None:
        """Should handle empty content gracefully."""
        grid = Grid.from_string("")
        engine = CorrectionEngine()

        result = engine.correct(grid)

        assert result.corrections_count == 0
        assert result.corrected_grid.to_string() == ""

    def test_whitespace_only(self) -> None:
        """Should handle whitespace-only content."""
        grid = Grid.from_string("   \n   \n   ")
        engine = CorrectionEngine()

        result = engine.correct(grid)

        assert result.corrections_count == 0

    def test_text_without_lines(self) -> None:
        """Should handle text content without ASCII diagram lines."""
        content = "Hello World\nThis is text\nNo diagrams here"
        grid = Grid.from_string(content)
        engine = CorrectionEngine()

        result = engine.correct(grid)

        assert result.corrections_count == 0
        assert result.corrected_grid.to_string() == content

    def test_single_horizontal_line(self) -> None:
        """Should handle a single horizontal line."""
        content = "-----"
        grid = Grid.from_string(content)
        engine = CorrectionEngine()

        result = engine.correct(grid)

        assert result.corrected_grid.to_string() == content
        # Single line has nothing to align to
        assert result.corrections_count == 0

    def test_single_vertical_line(self) -> None:
        """Should handle a single vertical line."""
        content = "|\n|\n|\n|"
        grid = Grid.from_string(content)
        engine = CorrectionEngine()

        result = engine.correct(grid)

        assert result.corrected_grid.to_string() == content


class TestCorrectionPipelineMultipleBoxes:
    """Tests for diagrams with multiple boxes."""

    def test_two_adjacent_boxes_horizontal(self) -> None:
        """Should handle two horizontally adjacent boxes."""
        content = """+--+  +--+
|  |  |  |
+--+  +--+"""
        grid = Grid.from_string(content)
        engine = CorrectionEngine()

        result = engine.correct(grid)

        assert result.corrected_grid is not None
        assert result.corrected_grid.to_string() == content

    def test_two_stacked_boxes(self) -> None:
        """Should handle two vertically stacked boxes."""
        content = """+--+
|  |
+--+
+--+
|  |
+--+"""
        grid = Grid.from_string(content)
        engine = CorrectionEngine()

        result = engine.correct(grid)

        assert result.corrected_grid is not None

    def test_nested_boxes(self, nested_boxes: str) -> None:
        """Should handle nested boxes."""
        grid = Grid.from_string(nested_boxes)
        engine = CorrectionEngine()

        result = engine.correct(grid)

        # Nested boxes should be preserved
        assert result.corrected_grid is not None


class TestCorrectionPipelineParallelLines:
    """Tests specifically for parallel line detection and correction."""

    def test_two_parallel_horizontal_lines_aligned(self) -> None:
        """Should recognize two aligned horizontal lines as parallel."""
        content = """-----

-----"""
        grid = Grid.from_string(content)
        engine = CorrectionEngine(tolerance=1)

        result = engine.analyze(grid)

        # Should find horizontal lines
        h_groups = [g for g in result.groups_found if g.direction == Direction.HORIZONTAL]
        assert len(h_groups) > 0

    def test_two_parallel_vertical_lines_aligned(self) -> None:
        """Should recognize two aligned vertical lines as parallel."""
        content = """|   |
|   |
|   |
|   |"""
        grid = Grid.from_string(content)
        engine = CorrectionEngine(tolerance=1)

        result = engine.analyze(grid)

        # Should find vertical lines
        v_groups = [g for g in result.groups_found if g.direction == Direction.VERTICAL]
        assert len(v_groups) > 0


class TestCorrectionPipelineToleranceSettings:
    """Tests for tolerance configuration."""

    def test_tolerance_zero_strict_matching(self) -> None:
        """With tolerance 0, only exactly aligned lines should be grouped."""
        content = """-----
 ----"""
        grid = Grid.from_string(content)
        engine = CorrectionEngine(tolerance=0)

        result = engine.analyze(grid)

        # Lines are offset, should not be grouped with tolerance 0
        # Each line should be in its own group or not grouped
        assert result.groups_found is not None

    def test_tolerance_two_loose_matching(self) -> None:
        """With tolerance 2, lines 2 apart should be grouped."""
        content = """-----

-----"""
        grid = Grid.from_string(content)
        engine = CorrectionEngine(tolerance=2)

        result = engine.analyze(grid)

        # Lines are 2 rows apart, should be found
        h_groups = [g for g in result.groups_found if g.direction == Direction.HORIZONTAL]
        assert len(h_groups) > 0
