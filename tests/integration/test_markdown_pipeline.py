"""Integration tests for the Markdown correction pipeline."""

from pathlib import Path

import pytest

from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.io import (
    BackupManager,
    DiagramClassifier,
    MarkdownCorrector,
    MarkdownParser,
)


@pytest.fixture
def pipeline() -> MarkdownCorrector:
    """Create full Markdown correction pipeline."""
    return MarkdownCorrector(
        parser=MarkdownParser(),
        classifier=DiagramClassifier(),
        engine=CorrectionEngine(tolerance=1, min_line_length=2),
    )


class TestMarkdownPipelineRoundTrip:
    """Full parse-correct-reassemble pipeline tests."""

    def test_simple_diagram_fixture(
        self, pipeline: MarkdownCorrector, markdown_dir: Path
    ) -> None:
        """Should process simple_diagram.md fixture."""
        text = (markdown_dir / "simple_diagram.md").read_text()
        result = pipeline.correct(text)

        assert result.blocks_found >= 1
        assert "# Simple Diagram" in result.corrected_text
        assert "End of document." in result.corrected_text

    def test_broken_diagram_fixture(
        self, pipeline: MarkdownCorrector, markdown_dir: Path
    ) -> None:
        """Should detect and correct broken_diagram.md fixture."""
        text = (markdown_dir / "broken_diagram.md").read_text()
        result = pipeline.correct(text)

        assert result.blocks_found >= 1
        assert "# Broken Diagram" in result.corrected_text
        assert "This should be corrected." in result.corrected_text

    def test_mixed_blocks_fixture(
        self, pipeline: MarkdownCorrector, markdown_dir: Path
    ) -> None:
        """Should handle mixed_blocks.md with code and diagrams."""
        text = (markdown_dir / "mixed_blocks.md").read_text()
        result = pipeline.correct(text)

        # Should find only the diagram block, not python/js
        assert result.blocks_found >= 1
        # Non-diagram code preserved
        assert 'print("world")' in result.corrected_text
        assert 'console.log("test")' in result.corrected_text

    def test_no_diagrams_fixture(
        self, pipeline: MarkdownCorrector, markdown_dir: Path
    ) -> None:
        """Should handle no_diagrams.md gracefully."""
        text = (markdown_dir / "no_diagrams.md").read_text()
        result = pipeline.correct(text)

        assert result.blocks_found == 0
        assert result.blocks_corrected == 0

    def test_multiple_diagrams_fixture(
        self, pipeline: MarkdownCorrector, markdown_dir: Path
    ) -> None:
        """Should process multiple_diagrams.md with two diagrams."""
        text = (markdown_dir / "multiple_diagrams.md").read_text()
        result = pipeline.correct(text)

        assert result.blocks_found == 2


class TestMarkdownPipelinePreservation:
    """Tests that the pipeline preserves document structure."""

    def test_preserves_headings(self, pipeline: MarkdownCorrector) -> None:
        text = "# H1\n## H2\n```\n+--+\n|  |\n+--+\n```\n### H3"
        result = pipeline.correct(text)
        assert "# H1" in result.corrected_text
        assert "## H2" in result.corrected_text
        assert "### H3" in result.corrected_text

    def test_preserves_paragraphs(self, pipeline: MarkdownCorrector) -> None:
        text = "Paragraph one.\n\n```\n+--+\n|  |\n+--+\n```\n\nParagraph two."
        result = pipeline.correct(text)
        assert "Paragraph one." in result.corrected_text
        assert "Paragraph two." in result.corrected_text

    def test_preserves_fence_language(self, pipeline: MarkdownCorrector) -> None:
        text = "```ascii\n+--+\n|  |\n+--+\n```"
        result = pipeline.correct(text)
        assert "```ascii" in result.corrected_text

    def test_empty_document(self, pipeline: MarkdownCorrector) -> None:
        result = pipeline.correct("")
        assert result.corrected_text == ""
        assert result.blocks_found == 0


class TestMarkdownPipelineWithBackup:
    """Integration tests for backup creation in the pipeline."""

    def test_backup_and_correct_workflow(self, tmp_path: Path) -> None:
        """Test the full workflow: backup, correct, verify."""
        md_file = tmp_path / "test.md"
        original = "```\n+----+\n|    |\n +---+\n```\n"
        md_file.write_text(original)

        # Create backup
        backup_manager = BackupManager()
        backup_path = backup_manager.create_backup(md_file)
        assert backup_path.read_text() == original

        # Correct
        pipeline = MarkdownCorrector(
            parser=MarkdownParser(),
            classifier=DiagramClassifier(),
            engine=CorrectionEngine(tolerance=1, min_line_length=2),
        )
        result = pipeline.correct(original)
        md_file.write_text(result.corrected_text)

        # Verify backup is untouched
        assert backup_path.read_text() == original
        # Verify file was modified
        assert md_file.exists()
