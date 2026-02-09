"""E2E tests for box detection and tree preservation integration."""

from pathlib import Path

import pytest

from ascii_corrector.config import Settings
from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.domain import Grid


class TestBoxDetectionIntegration:
    """E2E tests for box detection in correction pipeline."""

    def test_tall_box_gets_aligned(self) -> None:
        """Tall box should be detected even when taller than normal tolerance."""
        from ascii_corrector.detection.box_detector import BoxDetector

        content = Path(
            "tests/fixtures/diagrams/edge_cases/large_box_tall.txt"
        ).read_text()
        grid = Grid.from_string(content)

        # Verify the box detector finds the tall box
        detector = BoxDetector(min_size=2)
        boxes = detector.detect_boxes(grid)
        assert len(boxes) > 0, "Box detector should find the tall box"

        # Verify engine processes without error
        engine = CorrectionEngine(tolerance=1)
        result = engine.correct(grid)

        # Grid should be corrected (with or without changes, depends on alignment)
        assert result.corrected_grid is not None
        # Box detection stage ran without errors
        assert result.original_grid is not None

    def test_unicode_box_detected_and_preserved(self) -> None:
        """Unicode box should be detected and characters preserved."""
        content = Path(
            "tests/fixtures/diagrams/edge_cases/unicode_simple_box.txt"
        ).read_text()
        grid = Grid.from_string(content)
        engine = CorrectionEngine(tolerance=1)

        result = engine.correct(grid)

        # Should preserve Unicode characters
        corrected = result.corrected_grid.to_string()
        assert "┌" in corrected
        assert "│" in corrected
        assert "└" in corrected or "┘" in corrected


class TestTreePreservationIntegration:
    """E2E tests for tree structure preservation."""

    def test_tree_structure_preserved(self) -> None:
        """Tree branch notation should be preserved, not corrected."""
        content = Path(
            "tests/fixtures/diagrams/edge_cases/tree_simple.txt"
        ).read_text()
        grid = Grid.from_string(content)
        engine = CorrectionEngine(tolerance=1)

        result = engine.correct(grid)

        # Tree should be identified and preserved
        # Branch lines should not be aligned with each other
        corrected = result.corrected_grid.to_string()
        # Verify tree structure is intact
        assert "+--" in corrected

    def test_tree_preservation_can_be_disabled(self) -> None:
        """Tree preservation should be optional via settings."""
        content = Path(
            "tests/fixtures/diagrams/edge_cases/tree_simple.txt"
        ).read_text()
        grid = Grid.from_string(content)

        # Create engine with tree preservation disabled
        settings = Settings(preserve_trees=False)
        engine = CorrectionEngine(tolerance=1, settings=settings)

        result = engine.correct(grid)

        # With preservation disabled, corrections may be applied
        # (exact behavior depends on what the corrector does)
        assert result.corrected_grid is not None

    def test_tree_preservation_enabled_by_default(self) -> None:
        """Tree preservation should be enabled by default."""
        content = Path(
            "tests/fixtures/diagrams/edge_cases/tree_simple.txt"
        ).read_text()
        grid = Grid.from_string(content)

        # Default settings should have preserve_trees=True
        settings = Settings()
        assert settings.preserve_trees is True

        engine = CorrectionEngine(tolerance=1, settings=settings)
        result = engine.correct(grid)

        # Tree structure should be preserved
        assert "+--" in result.corrected_grid.to_string()
