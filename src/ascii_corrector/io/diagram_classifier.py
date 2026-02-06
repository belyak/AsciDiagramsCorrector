"""Classifier to determine if text content is an ASCII diagram."""

from ascii_corrector.domain.character import (
    _ARROW_CHARS,
    _CORNER_CHARS,
    _HORIZONTAL_CHARS,
    _JUNCTION_CHARS,
    _VERTICAL_CHARS,
)

_DIAGRAM_CHARS: frozenset[str] = (
    _HORIZONTAL_CHARS | _VERTICAL_CHARS | _CORNER_CHARS | _JUNCTION_CHARS | _ARROW_CHARS
)


class DiagramClassifier:
    """Determines whether a code block contains an ASCII diagram."""

    def __init__(
        self,
        diagram_languages: list[str] | None = None,
        min_char_ratio: float = 0.05,
    ) -> None:
        if diagram_languages is None:
            diagram_languages = ["", "ascii", "text", "diagram", "art"]
        self._diagram_languages = {lang.lower() for lang in diagram_languages}
        self._min_char_ratio = min_char_ratio

    def is_candidate_language(self, language: str) -> bool:
        """Check if a code block language label is a candidate for diagram content."""
        return language.lower() in self._diagram_languages

    def is_diagram(self, content: str, language: str) -> bool:
        """Determine if content is an ASCII diagram based on language and character ratio."""
        if not self.is_candidate_language(language):
            return False

        non_whitespace = [ch for ch in content if not ch.isspace()]
        if not non_whitespace:
            return False

        diagram_count = sum(1 for ch in non_whitespace if ch in _DIAGRAM_CHARS)
        ratio = diagram_count / len(non_whitespace)
        return ratio >= self._min_char_ratio
