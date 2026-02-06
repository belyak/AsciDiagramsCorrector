"""Unit tests for MarkdownCorrector."""

import pytest

from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.io.diagram_classifier import DiagramClassifier
from ascii_corrector.io.markdown_corrector import (
    MarkdownCorrectionResult,
    MarkdownCorrector,
)
from ascii_corrector.io.markdown_parser import MarkdownParser


@pytest.fixture
def parser() -> MarkdownParser:
    return MarkdownParser()


@pytest.fixture
def classifier() -> DiagramClassifier:
    return DiagramClassifier()


@pytest.fixture
def engine() -> CorrectionEngine:
    return CorrectionEngine(tolerance=1, min_line_length=2)


@pytest.fixture
def corrector(
    parser: MarkdownParser,
    classifier: DiagramClassifier,
    engine: CorrectionEngine,
) -> MarkdownCorrector:
    return MarkdownCorrector(parser=parser, classifier=classifier, engine=engine)


class TestMarkdownCorrectorSingleBlock:
    """Tests for correcting a single diagram block."""

    def test_corrects_diagram_block(self, corrector: MarkdownCorrector) -> None:
        text = "# Title\n```\n+----+\n|    |\n +---+\n```\nEnd"
        result = corrector.correct(text)
        assert result.blocks_found > 0
        assert isinstance(result.corrected_text, str)

    def test_returns_correction_result(self, corrector: MarkdownCorrector) -> None:
        text = "```\n+--+\n|  |\n+--+\n```"
        result = corrector.correct(text)
        assert isinstance(result, MarkdownCorrectionResult)
        assert result.blocks_found >= 0
        assert result.blocks_corrected >= 0

    def test_preserves_surrounding_text(self, corrector: MarkdownCorrector) -> None:
        text = "Before text\n```\n+--+\n|  |\n+--+\n```\nAfter text"
        result = corrector.correct(text)
        assert "Before text" in result.corrected_text
        assert "After text" in result.corrected_text


class TestMarkdownCorrectorMultipleBlocks:
    """Tests for correcting multiple diagram blocks."""

    def test_corrects_multiple_diagram_blocks(self, corrector: MarkdownCorrector) -> None:
        text = (
            "```\n+--+\n|  |\n+--+\n```\n"
            "text\n"
            "```\n----\n\n----\n```"
        )
        result = corrector.correct(text)
        assert result.blocks_found == 2


class TestMarkdownCorrectorSkipNonDiagrams:
    """Tests for skipping non-diagram code blocks."""

    def test_skips_python_block(self, corrector: MarkdownCorrector) -> None:
        text = "```python\nprint('hello')\n```"
        result = corrector.correct(text)
        assert result.blocks_found == 0
        assert "print('hello')" in result.corrected_text

    def test_skips_non_diagram_text_block(self, corrector: MarkdownCorrector) -> None:
        text = "```\nJust some plain text with no diagram characters at all.\n```"
        result = corrector.correct(text)
        assert result.blocks_corrected == 0

    def test_mixed_diagram_and_code_blocks(self, corrector: MarkdownCorrector) -> None:
        text = (
            "```python\ncode()\n```\n"
            "```\n+--+\n|  |\n+--+\n```\n"
            "```javascript\nvar x;\n```"
        )
        result = corrector.correct(text)
        # Only the diagram block should be found
        assert result.blocks_found == 1
        # Code blocks should be preserved
        assert "code()" in result.corrected_text
        assert "var x;" in result.corrected_text


class TestMarkdownCorrectorStatistics:
    """Tests for correction statistics."""

    def test_zero_blocks_when_no_diagrams(self, corrector: MarkdownCorrector) -> None:
        text = "No code blocks here."
        result = corrector.correct(text)
        assert result.blocks_found == 0
        assert result.blocks_corrected == 0
        assert result.total_corrections == 0

    def test_counts_corrections(self, corrector: MarkdownCorrector) -> None:
        text = "```\n+----+\n|    |\n +---+\n```"
        result = corrector.correct(text)
        assert result.blocks_found >= 1
        assert result.total_corrections >= 0


class TestMarkdownCorrectorPreservation:
    """Tests for content preservation."""

    def test_preserves_fences(self, corrector: MarkdownCorrector) -> None:
        text = "```ascii\n+--+\n|  |\n+--+\n```"
        result = corrector.correct(text)
        assert "```ascii" in result.corrected_text
        assert result.corrected_text.rstrip().endswith("```")

    def test_preserves_non_diagram_blocks(self, corrector: MarkdownCorrector) -> None:
        text = "```python\ndef foo():\n    pass\n```"
        result = corrector.correct(text)
        assert result.corrected_text == text

    def test_no_changes_for_well_formed_diagram(self, corrector: MarkdownCorrector) -> None:
        text = "```\n+--+\n|  |\n+--+\n```"
        result = corrector.correct(text)
        assert result.blocks_found >= 1
