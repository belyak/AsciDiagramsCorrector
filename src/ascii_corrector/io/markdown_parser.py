"""Markdown parser for extracting and replacing fenced code blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})([a-zA-Z0-9_+\-]*)\s*$")


@dataclass
class CodeBlock:
    """A fenced code block extracted from a Markdown document."""

    language: str
    content: str
    start_line: int
    end_line: int
    fence_char: str
    fence_indent: str

    @property
    def content_start_line(self) -> int:
        """Line index where content begins (after opening fence)."""
        return self.start_line + 1


@dataclass
class MarkdownDocument:
    """Parsed Markdown document with code block metadata."""

    text: str
    code_blocks: list[CodeBlock] = field(default_factory=list)

    def replace_content(self, block_index: int, new_content: str) -> str:
        """Replace the content of a code block and return the full text."""
        if block_index < 0 or block_index >= len(self.code_blocks):
            raise IndexError(f"Block index {block_index} out of range")

        block = self.code_blocks[block_index]
        lines = self.text.split("\n")

        # Replace lines between opening and closing fence
        content_start = block.content_start_line
        content_end = block.end_line  # exclusive: the closing fence line

        new_content_lines = new_content.split("\n") if new_content else []
        lines[content_start:content_end] = new_content_lines

        return "\n".join(lines)


class MarkdownParser:
    """Parses Markdown text to extract fenced code blocks."""

    def parse(self, text: str) -> MarkdownDocument:
        """Parse Markdown text and extract fenced code blocks."""
        lines = text.split("\n")
        code_blocks: list[CodeBlock] = []
        i = 0

        while i < len(lines):
            match = _FENCE_RE.match(lines[i])
            if match:
                indent = match.group(1)
                fence = match.group(2)
                language = match.group(3)
                fence_char = fence[0]
                fence_len = len(fence)
                open_line = i

                # Find matching closing fence
                j = i + 1
                while j < len(lines):
                    close_match = _FENCE_RE.match(lines[j])
                    if (
                        close_match
                        and close_match.group(2)[0] == fence_char
                        and len(close_match.group(2)) >= fence_len
                        and close_match.group(3) == ""
                    ):
                        # Found closing fence
                        content_lines = lines[open_line + 1 : j]
                        content = "\n".join(content_lines)
                        code_blocks.append(
                            CodeBlock(
                                language=language,
                                content=content,
                                start_line=open_line,
                                end_line=j,
                                fence_char=fence_char,
                                fence_indent=indent,
                            )
                        )
                        i = j + 1
                        break
                    j += 1
                else:
                    # No closing fence found, skip
                    i += 1
            else:
                i += 1

        return MarkdownDocument(text=text, code_blocks=code_blocks)
