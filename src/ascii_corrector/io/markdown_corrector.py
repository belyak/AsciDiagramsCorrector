"""Orchestrator for correcting ASCII diagrams within Markdown documents."""

from __future__ import annotations

from dataclasses import dataclass

from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.domain import Grid
from ascii_corrector.io.diagram_classifier import DiagramClassifier
from ascii_corrector.io.markdown_parser import MarkdownParser


@dataclass
class MarkdownCorrectionResult:
    """Result of correcting diagrams in a Markdown document."""

    corrected_text: str
    blocks_found: int
    blocks_corrected: int
    total_corrections: int


class MarkdownCorrector:
    """Corrects ASCII diagrams embedded in Markdown code blocks."""

    def __init__(
        self,
        parser: MarkdownParser,
        classifier: DiagramClassifier,
        engine: CorrectionEngine,
    ) -> None:
        self._parser = parser
        self._classifier = classifier
        self._engine = engine

    def correct(self, text: str) -> MarkdownCorrectionResult:
        """Parse Markdown, correct diagram blocks, return result."""
        doc = self._parser.parse(text)

        # Identify diagram blocks
        diagram_indices: list[int] = []
        for i, block in enumerate(doc.code_blocks):
            if self._classifier.is_diagram(block.content, block.language):
                diagram_indices.append(i)

        blocks_found = len(diagram_indices)
        blocks_corrected = 0
        total_corrections = 0

        # Process in reverse order so line shifts don't invalidate later positions
        result_text = text
        for idx in reversed(diagram_indices):
            block = doc.code_blocks[idx]
            grid = Grid.from_string(block.content)
            correction_result = self._engine.correct(grid)

            corrected_content = correction_result.corrected_grid.to_string()
            if correction_result.corrections_count > 0:
                blocks_corrected += 1
                total_corrections += correction_result.corrections_count

            # Re-parse to get updated positions after each replacement
            current_doc = self._parser.parse(result_text)
            result_text = current_doc.replace_content(idx, corrected_content)

        return MarkdownCorrectionResult(
            corrected_text=result_text,
            blocks_found=blocks_found,
            blocks_corrected=blocks_corrected,
            total_corrections=total_corrections,
        )
