"""Correct command for ASCII diagram correction."""

from pathlib import Path
from typing import Optional

import typer

from ascii_corrector.config import Settings
from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.domain import Grid
from ascii_corrector.logging import get_logger

app = typer.Typer(help="Correct ASCII diagrams.")
logger = get_logger(__name__)


@app.callback(invoke_without_command=True)
def correct(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Argument(
        None,
        help="Input ASCII diagram file",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (default: stdout)",
    ),
    in_place: bool = typer.Option(
        False,
        "--in-place",
        "-i",
        help="Modify input file in place",
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
    Correct shifted parallel lines in an ASCII diagram.

    Examples:
        ascii-corrector correct diagram.txt
        ascii-corrector correct diagram.txt -o fixed.txt
        ascii-corrector correct diagram.txt --dry-run
    """
    settings = Settings(tolerance=tolerance, dry_run=dry_run)

    # Read input
    if input_file is None:
        typer.echo("Error: Input file required", err=True)
        raise typer.Exit(1)

    content = input_file.read_text(encoding=settings.default_encoding)
    logger.info("reading_file", path=str(input_file))

    # Parse into grid
    grid = Grid.from_string(content)

    # Create correction engine
    engine = CorrectionEngine(
        tolerance=settings.tolerance,
        min_line_length=settings.min_line_length,
    )

    if dry_run:
        # Analyze only
        result = engine.analyze(grid)
        typer.echo("Dry run mode - analysis only")
        typer.echo(f"Lines detected: {sum(len(g.lines) for g in result.groups_found)}")
        typer.echo(f"Parallel groups found: {len(result.groups_found)}")
        typer.echo(f"Corrections needed: {result.corrections_count}")

        if result.corrections_count > 0:
            typer.echo("\nCorrections that would be applied:")
            for corr in result.corrections_applied:
                direction = corr.line.direction.name.lower()
                if corr.row_offset != 0:
                    typer.echo(
                        f"  - Move {direction} line at row "
                        f"{corr.line.dominant_row()} by {corr.row_offset} rows"
                    )
                if corr.col_offset != 0:
                    typer.echo(
                        f"  - Move {direction} line at col "
                        f"{corr.line.dominant_col()} by {corr.col_offset} cols"
                    )
        return

    # Apply corrections
    result = engine.correct(grid)
    corrected = result.corrected_grid.to_string()

    logger.info(
        "corrections_applied",
        count=result.corrections_count,
        groups=len(result.groups_found),
    )

    # Write output
    if in_place and input_file:
        input_file.write_text(corrected, encoding=settings.default_encoding)
        typer.echo(f"Corrected diagram written to {input_file}")
        typer.echo(f"Applied {result.corrections_count} corrections")
    elif output_file:
        output_file.write_text(corrected, encoding=settings.default_encoding)
        typer.echo(f"Corrected diagram written to {output_file}")
        typer.echo(f"Applied {result.corrections_count} corrections")
    else:
        typer.echo(corrected)
