"""Shared pytest fixtures for ASCII Corrector tests."""

from pathlib import Path

import pytest

# --- Path Fixtures ---


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def diagrams_dir(fixtures_dir: Path) -> Path:
    """Return path to diagram fixtures directory."""
    return fixtures_dir / "diagrams"


# --- Simple Diagram Fixtures ---


@pytest.fixture
def simple_box() -> str:
    """A simple well-formed box."""
    return "+--+\n|  |\n+--+"


@pytest.fixture
def simple_box_lines() -> list[str]:
    """Simple box as a list of strings (grid format)."""
    return [
        "+--+",
        "|  |",
        "+--+",
    ]


@pytest.fixture
def broken_box_missing_corner() -> str:
    """A box with missing bottom-right corner."""
    return "+--+\n|  |\n+-- "


@pytest.fixture
def broken_box_shifted_bottom() -> str:
    """A box with shifted bottom line."""
    return "+----+\n|    |\n +---+"


@pytest.fixture
def nested_boxes() -> str:
    """Nested box structure."""
    return """+--------+
| +----+ |
| |    | |
| +----+ |
+--------+"""


@pytest.fixture
def parallel_lines_shifted() -> str:
    """Two parallel horizontal lines with one shifted."""
    return """-----

 ----"""


# --- Markdown Path Fixtures ---


@pytest.fixture
def markdown_dir(fixtures_dir: Path) -> Path:
    """Return path to markdown fixtures directory."""
    return fixtures_dir / "markdown"


# --- Temporary File Fixtures ---


@pytest.fixture
def temp_diagram_file(tmp_path: Path):
    """Factory fixture to create temporary diagram files."""

    def _create(content: str, filename: str = "diagram.txt") -> Path:
        file = tmp_path / filename
        file.write_text(content)
        return file

    return _create


@pytest.fixture
def temp_markdown_file(tmp_path: Path):
    """Factory fixture to create temporary Markdown files."""

    def _create(content: str, filename: str = "document.md") -> Path:
        file = tmp_path / filename
        file.write_text(content)
        return file

    return _create


# --- Marker Configuration ---


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line(
        "markers", "integration: Integration tests (component interactions)"
    )
    config.addinivalue_line("markers", "e2e: End-to-end tests (full pipeline)")
    config.addinivalue_line(
        "markers", "slow: Slow tests (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "external: Tests requiring external services (Claude CLI)"
    )
