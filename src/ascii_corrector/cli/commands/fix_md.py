"""Fix-md command for correcting ASCII diagrams in Markdown files."""

from pathlib import Path

import typer

from ascii_corrector.config import Settings
from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.io import (
    BackupManager,
    DiagramClassifier,
    MarkdownCorrector,
    MarkdownParser,
)
from ascii_corrector.logging import get_logger

app = typer.Typer(help="Fix ASCII diagrams in Markdown files.")
logger = get_logger(__name__)


@app.callback(invoke_without_command=True)
def fix_md(
    ctx: typer.Context,
    input_files: list[Path] = typer.Argument(
        ...,
        help="Markdown files to process",
    ),
    no_backup: bool = typer.Option(
        False,
        "--no-backup",
        help="Skip creating .bak backup file",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be changed without applying",
    ),
    tolerance: int = typer.Option(
        1,
        "--tolerance",
        "-t",
        help="Row/column tolerance for parallel detection",
        min=0,
        max=5,
    ),
) -> None:
    """
    Correct ASCII diagrams embedded in Markdown files.

    Detects fenced code blocks containing ASCII diagrams, corrects them
    using the correction engine, and writes the result in-place.

    Examples:
        ascii-corrector fix-md README.md
        ascii-corrector fix-md doc1.md doc2.md --no-backup
        ascii-corrector fix-md README.md --dry-run
    """
    settings = Settings(tolerance=tolerance, dry_run=dry_run)

    parser = MarkdownParser()
    classifier = DiagramClassifier(
        diagram_languages=settings.diagram_languages,
        min_char_ratio=settings.min_diagram_char_ratio,
    )
    engine = CorrectionEngine(
        tolerance=settings.tolerance,
        min_line_length=settings.min_line_length,
    )
    corrector = MarkdownCorrector(parser=parser, classifier=classifier, engine=engine)
    backup_manager = BackupManager(suffix=settings.backup_suffix)

    for input_file in input_files:
        logger.info("processing_file", path=str(input_file))
        content = input_file.read_text(encoding=settings.default_encoding)

        result = corrector.correct(content)

        if result.blocks_found == 0:
            typer.echo(f"{input_file}: no diagram blocks found")
            continue

        if dry_run:
            typer.echo(f"{input_file}: {result.blocks_found} diagram block(s) found")
            typer.echo(f"  {result.blocks_corrected} block(s) would be corrected")
            typer.echo(f"  {result.total_corrections} total correction(s)")
            continue

        if not no_backup:
            backup_path = backup_manager.create_backup(input_file)
            logger.info("backup_created", path=str(backup_path))
            typer.echo(f"{input_file}: backup saved to {backup_path}")

        input_file.write_text(result.corrected_text, encoding=settings.default_encoding)

        typer.echo(
            f"{input_file}: corrected {result.blocks_corrected} of "
            f"{result.blocks_found} diagram block(s) "
            f"({result.total_corrections} correction(s))"
        )
