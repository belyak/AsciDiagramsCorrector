"""Unit tests for DiagramClassifier."""


from ascii_corrector.io.diagram_classifier import DiagramClassifier


class TestDiagramClassifierLanguageMatching:
    """Tests for language label matching."""

    def test_empty_language_is_candidate(self) -> None:
        """Empty language label should be a candidate for diagram."""
        classifier = DiagramClassifier(diagram_languages=["", "ascii"])
        assert classifier.is_candidate_language("") is True

    def test_ascii_language_is_candidate(self) -> None:
        classifier = DiagramClassifier(diagram_languages=["", "ascii"])
        assert classifier.is_candidate_language("ascii") is True

    def test_python_language_is_not_candidate(self) -> None:
        classifier = DiagramClassifier(diagram_languages=["", "ascii"])
        assert classifier.is_candidate_language("python") is False

    def test_language_matching_is_case_insensitive(self) -> None:
        classifier = DiagramClassifier(diagram_languages=["ascii", "text"])
        assert classifier.is_candidate_language("ASCII") is True
        assert classifier.is_candidate_language("Text") is True

    def test_all_default_languages(self) -> None:
        classifier = DiagramClassifier()
        for lang in ["", "ascii", "text", "diagram", "art"]:
            assert classifier.is_candidate_language(lang) is True


class TestDiagramClassifierCharRatio:
    """Tests for character ratio heuristic."""

    def test_box_diagram_has_high_ratio(self) -> None:
        content = "+--+\n|  |\n+--+"
        classifier = DiagramClassifier(min_char_ratio=0.05)
        assert classifier.is_diagram(content, "") is True

    def test_plain_text_has_low_ratio(self) -> None:
        content = "Hello world this is just plain text."
        classifier = DiagramClassifier(min_char_ratio=0.05)
        assert classifier.is_diagram(content, "") is False

    def test_empty_content_is_not_diagram(self) -> None:
        classifier = DiagramClassifier()
        assert classifier.is_diagram("", "") is False

    def test_whitespace_only_is_not_diagram(self) -> None:
        classifier = DiagramClassifier()
        assert classifier.is_diagram("   \n   ", "") is False

    def test_code_block_with_wrong_language_is_not_diagram(self) -> None:
        content = "+--+\n|  |\n+--+"
        classifier = DiagramClassifier()
        assert classifier.is_diagram(content, "python") is False

    def test_horizontal_lines_detected(self) -> None:
        content = "-------\n\n-------"
        classifier = DiagramClassifier(min_char_ratio=0.05)
        assert classifier.is_diagram(content, "") is True

    def test_vertical_lines_detected(self) -> None:
        content = "|\n|\n|\n|\n|"
        classifier = DiagramClassifier(min_char_ratio=0.05)
        assert classifier.is_diagram(content, "") is True

    def test_mixed_content_below_threshold(self) -> None:
        content = "This is mostly text with one - dash."
        classifier = DiagramClassifier(min_char_ratio=0.3)
        assert classifier.is_diagram(content, "") is False

    def test_custom_ratio_threshold(self) -> None:
        content = "a-b"
        classifier_low = DiagramClassifier(min_char_ratio=0.01)
        classifier_high = DiagramClassifier(min_char_ratio=0.9)
        assert classifier_low.is_diagram(content, "") is True
        assert classifier_high.is_diagram(content, "") is False


class TestDiagramClassifierEdgeCases:
    """Edge case tests."""

    def test_single_line_char(self) -> None:
        classifier = DiagramClassifier(min_char_ratio=0.05)
        assert classifier.is_diagram("-", "") is True

    def test_corner_and_junction_chars_count(self) -> None:
        content = "+*+\n* *\n+*+"
        classifier = DiagramClassifier(min_char_ratio=0.05)
        assert classifier.is_diagram(content, "") is True

    def test_arrow_chars_count(self) -> None:
        content = "-->  <--  ^  v"
        classifier = DiagramClassifier(min_char_ratio=0.05)
        assert classifier.is_diagram(content, "") is True
