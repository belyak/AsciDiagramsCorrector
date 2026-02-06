"""End-to-end tests for the fix-md CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from ascii_corrector.cli.app import app

runner = CliRunner()


class TestFixMdCommandBasic:
    """Basic tests for the fix-md command."""

    def test_fix_md_processes_file(self, temp_markdown_file) -> None:
        """Should process a Markdown file with a diagram."""
        content = "# Title\n```\n+--+\n|  |\n+--+\n```\n"
        input_file = temp_markdown_file(content)

        result = runner.invoke(app, ["fix-md", str(input_file)])

        assert result.exit_code == 0

    def test_fix_md_creates_backup(self, temp_markdown_file) -> None:
        """Should create a .bak backup file by default."""
        content = "# Title\n```\n+--+\n|  |\n+--+\n```\n"
        input_file = temp_markdown_file(content)

        result = runner.invoke(app, ["fix-md", str(input_file)])

        assert result.exit_code == 0
        backup = input_file.parent / (input_file.name + ".bak")
        assert backup.exists()
        assert backup.read_text() == content

    def test_fix_md_no_backup_option(self, temp_markdown_file) -> None:
        """Should skip backup when --no-backup is used."""
        content = "# Title\n```\n+--+\n|  |\n+--+\n```\n"
        input_file = temp_markdown_file(content)

        result = runner.invoke(app, ["fix-md", "--no-backup", str(input_file)])

        assert result.exit_code == 0
        backup = input_file.parent / (input_file.name + ".bak")
        assert not backup.exists()

    def test_fix_md_no_diagram_blocks(self, temp_markdown_file) -> None:
        """Should report when no diagram blocks are found."""
        content = "# Title\n\nJust text.\n"
        input_file = temp_markdown_file(content)

        result = runner.invoke(app, ["fix-md", str(input_file)])

        assert result.exit_code == 0
        assert "no diagram blocks found" in result.stdout

    def test_fix_md_missing_file(self) -> None:
        """Should error on missing input file."""
        result = runner.invoke(app, ["fix-md", "nonexistent.md"])

        assert result.exit_code != 0

    def test_fix_md_multiple_files(self, tmp_path: Path) -> None:
        """Should process multiple files."""
        content = "```\n+--+\n|  |\n+--+\n```\n"
        file1 = tmp_path / "doc1.md"
        file1.write_text(content)
        file2 = tmp_path / "doc2.md"
        file2.write_text(content)

        result = runner.invoke(app, ["fix-md", str(file1), str(file2)])

        assert result.exit_code == 0


class TestFixMdCommandDryRun:
    """Tests for the --dry-run option."""

    def test_dry_run_shows_analysis(self, temp_markdown_file) -> None:
        """Dry run should show what would be changed."""
        content = "```\n+----+\n|    |\n +---+\n```\n"
        input_file = temp_markdown_file(content)

        result = runner.invoke(app, ["fix-md", "--dry-run", str(input_file)])

        assert result.exit_code == 0
        assert "diagram block(s) found" in result.stdout

    def test_dry_run_does_not_modify_file(self, temp_markdown_file) -> None:
        """Dry run should not modify the input file."""
        original = "```\n+----+\n|    |\n +---+\n```\n"
        input_file = temp_markdown_file(original)

        runner.invoke(app, ["fix-md", "-n", str(input_file)])

        assert input_file.read_text() == original

    def test_dry_run_does_not_create_backup(self, temp_markdown_file) -> None:
        """Dry run should not create backup."""
        content = "```\n+--+\n|  |\n+--+\n```\n"
        input_file = temp_markdown_file(content)

        runner.invoke(app, ["fix-md", "-n", str(input_file)])

        backup = input_file.parent / (input_file.name + ".bak")
        assert not backup.exists()


class TestFixMdCommandTolerance:
    """Tests for the --tolerance option."""

    def test_tolerance_option(self, temp_markdown_file) -> None:
        """Should accept tolerance option."""
        content = "```\n+--+\n|  |\n+--+\n```\n"
        input_file = temp_markdown_file(content)

        result = runner.invoke(
            app, ["fix-md", "--tolerance", "2", str(input_file)]
        )

        assert result.exit_code == 0

    def test_tolerance_short_option(self, temp_markdown_file) -> None:
        """Should accept short tolerance option -t."""
        content = "```\n+--+\n|  |\n+--+\n```\n"
        input_file = temp_markdown_file(content)

        result = runner.invoke(app, ["fix-md", "-t", "2", str(input_file)])

        assert result.exit_code == 0


class TestFixMdCommandWithBrokenDiagrams:
    """Tests for correcting broken diagrams in Markdown."""

    def test_preserves_non_diagram_content(self, temp_markdown_file) -> None:
        """Should preserve text and code blocks that are not diagrams."""
        content = (
            "# Title\n\n"
            "```python\ndef foo():\n    pass\n```\n\n"
            "```\n+--+\n|  |\n+--+\n```\n"
        )
        input_file = temp_markdown_file(content)

        runner.invoke(app, ["fix-md", "--no-backup", str(input_file)])

        result_text = input_file.read_text()
        assert "# Title" in result_text
        assert "def foo():" in result_text
        assert "    pass" in result_text
