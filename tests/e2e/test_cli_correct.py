"""End-to-end tests for the correct CLI command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ascii_corrector.cli.app import app

runner = CliRunner()


class TestCorrectCommandBasic:
    """Basic tests for the correct command."""

    def test_correct_file_to_stdout(self, temp_diagram_file) -> None:
        """Should output corrected diagram to stdout."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["correct", str(input_file)])

        assert result.exit_code == 0
        assert "+--+" in result.stdout

    def test_correct_file_to_output_file(self, temp_diagram_file, tmp_path: Path) -> None:
        """Should write corrected diagram to output file."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)
        output_file = tmp_path / "output.txt"

        result = runner.invoke(
            app, ["correct", "-o", str(output_file), str(input_file)]
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "+--+" in output_file.read_text()

    def test_correct_file_in_place(self, temp_diagram_file) -> None:
        """Should modify file in place when --in-place is used."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["correct", "--in-place", str(input_file)])

        assert result.exit_code == 0
        # File should be modified
        assert input_file.exists()
        assert "+--+" in input_file.read_text()

    def test_correct_missing_file(self) -> None:
        """Should error on missing input file."""
        result = runner.invoke(app, ["correct", "nonexistent.txt"])

        assert result.exit_code != 0

    def test_correct_without_file_argument(self) -> None:
        """Should error when no input file is provided."""
        result = runner.invoke(app, ["correct"])

        assert result.exit_code != 0


class TestCorrectCommandDryRun:
    """Tests for the --dry-run option."""

    def test_dry_run_shows_analysis(self, temp_diagram_file) -> None:
        """Dry run should show what would be changed."""
        content = "+----+\n|    |\n +---+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["correct", "--dry-run", str(input_file)])

        assert result.exit_code == 0
        assert "Dry run mode" in result.stdout
        assert "Lines detected" in result.stdout

    def test_dry_run_does_not_modify_file(self, temp_diagram_file) -> None:
        """Dry run should not modify the input file."""
        original_content = "+----+\n|    |\n +---+"
        input_file = temp_diagram_file(original_content)

        runner.invoke(app, ["correct", "--dry-run", str(input_file)])

        # File should be unchanged
        assert input_file.read_text() == original_content


class TestCorrectCommandTolerance:
    """Tests for the --tolerance option."""

    def test_tolerance_option(self, temp_diagram_file) -> None:
        """Should accept tolerance option."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(
            app, ["correct", "--tolerance", "2", str(input_file)]
        )

        assert result.exit_code == 0

    def test_tolerance_short_option(self, temp_diagram_file) -> None:
        """Should accept short tolerance option -t."""
        content = "+--+\n|  |\n+--+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["correct", "-t", "2", str(input_file)])

        assert result.exit_code == 0


class TestCorrectCommandWithBrokenDiagrams:
    """Tests for correcting broken diagrams."""

    def test_correct_shifted_bottom_line(self, temp_diagram_file) -> None:
        """Should process a box with shifted bottom line."""
        content = "+----+\n|    |\n +---+"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["correct", str(input_file)])

        assert result.exit_code == 0
        # Output should contain diagram content
        assert "+" in result.stdout or "-" in result.stdout

    def test_correct_diagram_with_text(self, temp_diagram_file) -> None:
        """Should handle diagrams mixed with text."""
        content = "Title\n+--+\n|  |\n+--+\nCaption"
        input_file = temp_diagram_file(content)

        result = runner.invoke(app, ["correct", str(input_file)])

        assert result.exit_code == 0
        assert "Title" in result.stdout
        assert "Caption" in result.stdout
