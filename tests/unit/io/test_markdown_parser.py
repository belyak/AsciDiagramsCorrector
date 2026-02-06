"""Unit tests for MarkdownParser."""

import pytest

from ascii_corrector.io.markdown_parser import (
    MarkdownParser,
)


class TestMarkdownParserFenceDetection:
    """Tests for detecting fenced code blocks."""

    def test_single_backtick_fence(self) -> None:
        text = "before\n```\ncode\n```\nafter"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 1

    def test_tilde_fence(self) -> None:
        text = "before\n~~~\ncode\n~~~\nafter"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 1

    def test_four_backtick_fence(self) -> None:
        text = "text\n````\ncode\n````\ntext"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 1

    def test_multiple_code_blocks(self) -> None:
        text = "# Title\n```\nblock1\n```\ntext\n```\nblock2\n```\n"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 2

    def test_no_code_blocks(self) -> None:
        text = "Just plain text\nwith no code blocks."
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 0

    def test_unclosed_fence_ignored(self) -> None:
        text = "text\n```\ncode without closing"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 0

    def test_mismatched_fence_types_ignored(self) -> None:
        text = "text\n```\ncode\n~~~\nmore"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 0

    def test_indented_fence(self) -> None:
        text = "text\n  ```\n  code\n  ```\ntext"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert len(doc.code_blocks) == 1


class TestMarkdownParserLanguageExtraction:
    """Tests for extracting language labels."""

    def test_language_label_extracted(self) -> None:
        text = "```python\nprint('hi')\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].language == "python"

    def test_empty_language_label(self) -> None:
        text = "```\ncode\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].language == ""

    def test_ascii_language_label(self) -> None:
        text = "```ascii\n+--+\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].language == "ascii"

    def test_language_with_plus(self) -> None:
        text = "```c++\nint main();\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].language == "c++"


class TestMarkdownParserContentExtraction:
    """Tests for extracting code block content."""

    def test_single_line_content(self) -> None:
        text = "```\nhello\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].content == "hello"

    def test_multi_line_content(self) -> None:
        text = "```\nline1\nline2\nline3\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].content == "line1\nline2\nline3"

    def test_empty_content(self) -> None:
        text = "```\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].content == ""

    def test_content_preserves_internal_blank_lines(self) -> None:
        text = "```\nline1\n\nline3\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[0].content == "line1\n\nline3"


class TestCodeBlockPositions:
    """Tests for code block line positions."""

    def test_start_and_end_lines(self) -> None:
        text = "before\n```\ncode\n```\nafter"
        parser = MarkdownParser()
        doc = parser.parse(text)
        block = doc.code_blocks[0]
        assert block.start_line == 1  # line index of opening fence
        assert block.end_line == 3    # line index of closing fence

    def test_content_start_line(self) -> None:
        text = "before\n```\ncode\n```\nafter"
        parser = MarkdownParser()
        doc = parser.parse(text)
        block = doc.code_blocks[0]
        assert block.content_start_line == 2

    def test_second_block_positions(self) -> None:
        text = "```\na\n```\ntext\n```\nb\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.code_blocks[1].start_line == 4
        assert doc.code_blocks[1].end_line == 6


class TestMarkdownDocumentReplace:
    """Tests for replacing code block content."""

    def test_replace_single_block(self) -> None:
        text = "before\n```\nold\n```\nafter"
        parser = MarkdownParser()
        doc = parser.parse(text)
        result = doc.replace_content(0, "new")
        assert "new" in result
        assert "before" in result
        assert "after" in result
        assert "old" not in result

    def test_replace_preserves_fences(self) -> None:
        text = "```ascii\nold\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        result = doc.replace_content(0, "new")
        assert result == "```ascii\nnew\n```"

    def test_replace_multiple_blocks_reverse_order(self) -> None:
        text = "```\nA\n```\nmid\n```\nB\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        # Replace second block first (reverse order)
        result = doc.replace_content(1, "B2")
        doc2 = parser.parse(result)
        result2 = doc2.replace_content(0, "A2")
        assert "A2" in result2
        assert "B2" in result2

    def test_replace_multiline_content(self) -> None:
        text = "```\nold1\nold2\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        result = doc.replace_content(0, "new1\nnew2\nnew3")
        assert "new1\nnew2\nnew3" in result

    def test_replace_out_of_range_raises(self) -> None:
        text = "```\ncode\n```"
        parser = MarkdownParser()
        doc = parser.parse(text)
        with pytest.raises(IndexError):
            doc.replace_content(5, "new")


class TestMarkdownParserRoundTrip:
    """Round-trip tests: parse then reassemble."""

    def test_no_blocks_roundtrip(self) -> None:
        text = "Just text.\nMore text."
        parser = MarkdownParser()
        doc = parser.parse(text)
        assert doc.text == text

    def test_with_block_no_changes_roundtrip(self) -> None:
        text = "before\n```\ncode\n```\nafter"
        parser = MarkdownParser()
        doc = parser.parse(text)
        result = doc.replace_content(0, "code")
        assert result == text
