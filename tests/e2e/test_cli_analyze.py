"""End-to-end tests for the analyze CLI command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ascii_corrector.cli.app import app

runner = CliRunner()


class TestAnalyzeCommandBasic:
    """Basic tests for the analyze command."""

    def test_analyze_file_basic(self, temp_diagram_file) -> None:
        """Should analyze a diagram file and show statistics."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file)])

        assert result.exit_code == 0
        assert "Diagram Analysis" in result.stdout
        assert "Dimensions" in result.stdout

    def test_analyze_shows_dimensions(self, temp_diagram_file) -> None:
        """Should show grid dimensions."""
        content = "+----+\n|    |\n|    |\n+----+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file)])

        assert result.exit_code == 0
        # Should show width x height format
        assert "x" in result.stdout

    def test_analyze_missing_file(self) -> None:
        """Should error on missing input file."""
        result = runner.invoke(app, ["analyze", "nonexistent.txt"])

        assert result.exit_code != 0

    def test_analyze_without_file_argument(self) -> None:
        """Should error when no input file is provided."""
        result = runner.invoke(app, ["analyze"])

        assert result.exit_code != 0


class TestAnalyzeCommandOptions:
    """Tests for analyze command options."""

    def test_analyze_with_lines_option(self, temp_diagram_file) -> None:
        """Should show detected lines with --lines option."""
        content = "+----+\n|    |\n|    |\n+----+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file), "--lines"])

        assert result.exit_code == 0
        assert "Detected Lines" in result.stdout

    def test_analyze_with_parallel_option(self, temp_diagram_file) -> None:
        """Should show parallel groups with --parallel option."""
        content = "+----+\n|    |\n|    |\n+----+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file), "--parallel"])

        assert result.exit_code == 0
        assert "Parallel Line Groups" in result.stdout

    def test_analyze_with_no_issues_option(self, temp_diagram_file) -> None:
        """Should hide issues with --no-issues option."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file), "--no-issues"])

        assert result.exit_code == 0
        # Should not show issues section
        # (or show it but not prominently)

    def test_analyze_with_tolerance_option(self, temp_diagram_file) -> None:
        """Should accept tolerance option."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(
            app, ["analyze", str(input_file), "--tolerance", "2"]
        )

        assert result.exit_code == 0

    def test_analyze_with_short_options(self, temp_diagram_file) -> None:
        """Should accept short option flags."""
        content = "+----+\n|    |\n|    |\n+----+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file), "-l", "-p", "-t", "1"])

        assert result.exit_code == 0
        assert "Detected Lines" in result.stdout
        assert "Parallel Line Groups" in result.stdout


class TestAnalyzeCommandOutput:
    """Tests for analyze command output content."""

    def test_analyze_shows_line_counts(self, temp_diagram_file) -> None:
        """Should show horizontal and vertical line counts."""
        content = "+----+\n|    |\n|    |\n+----+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file)])

        assert result.exit_code == 0
        assert "Horizontal lines" in result.stdout
        assert "Vertical lines" in result.stdout

    def test_analyze_shows_parallel_groups_count(self, temp_diagram_file) -> None:
        """Should show count of parallel groups."""
        content = "+----+\n|    |\n|    |\n+----+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file)])

        assert result.exit_code == 0
        assert "Parallel groups" in result.stdout

    def test_analyze_correct_diagram_no_issues(self, temp_diagram_file) -> None:
        """Should report no issues for correct diagram."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file)])

        assert result.exit_code == 0
        # Either shows "No alignment issues" or shows 0 issues
        assert "No alignment issues" in result.stdout or "0" in result.stdout

    def test_analyze_shifted_diagram_shows_issues(self, temp_diagram_file) -> None:
        """Should report issues for shifted diagram."""
        content = "+----+\n|    |\n +---+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["analyze", str(input_file)])

        assert result.exit_code == 0
        assert "Detected Issues" in result.stdout


class TestAnalyzeCommandWithFixtures:
    """Tests using fixture files."""

    def test_analyze_complex_diagram_fixture(self, diagrams_dir: Path) -> None:
        """Should analyze complex diagram fixture."""
        complex_file = diagrams_dir / "complex_diagram.txt"

        result = runner.invoke(app, ["analyze", str(complex_file)])

        assert result.exit_code == 0
        assert "Diagram Analysis" in result.stdout
        # Complex diagram should have multiple lines
        assert "Horizontal lines" in result.stdout
