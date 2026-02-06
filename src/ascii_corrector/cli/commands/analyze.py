"""Analyze command for ASCII diagram analysis."""

from pathlib import Path
from typing import Optional

import typer

from ascii_corrector.config import Settings
from ascii_corrector.correction import CorrectionEngine
from ascii_corrector.domain import Direction, Grid
from ascii_corrector.logging import get_logger

app = typer.Typer(help="Analyze ASCII diagrams without correcting.")
logger = get_logger(__name__)


@app.callback(invoke_without_command=True)
def analyze(
    ctx: typer.Context,
    input_file: Optional[Path] = typer.Argument(
        None,
        help="Input ASCII diagram file",
        exists=True,
        readable=True,
    ),
    show_lines: bool = typer.Option(
        False,
        "--lines",
        "-l",
        help="Show detected lines",
    ),
    show_parallel: bool = typer.Option(
        False,
        "--parallel",
        "-p",
        help="Show parallel line groups",
    ),
    show_issues: bool = typer.Option(
        True,
        "--issues/--no-issues",
        help="Show detected issues",
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
    Analyze an ASCII diagram and report detected issues.

    Examples:
        ascii-corrector analyze diagram.txt
        ascii-corrector analyze diagram.txt --lines
        ascii-corrector analyze diagram.txt --parallel
    """
    settings = Settings(tolerance=tolerance)

    # Read input
    if input_file is None:
        typer.echo("Error: Input file required", err=True)
        raise typer.Exit(1)

    content = input_file.read_text(encoding=settings.default_encoding)
    logger.info("analyzing_file", path=str(input_file))

    # Parse into grid
    grid = Grid.from_string(content)

    # Basic statistics
    lines_content = content.split("\n")
    typer.echo("Diagram Analysis")
    typer.echo("=" * 40)
    typer.echo(f"  Dimensions: {grid.width} x {grid.height}")
    typer.echo(f"  Total characters: {sum(len(line) for line in lines_content)}")

    # Create correction engine for analysis
    engine = CorrectionEngine(
        tolerance=settings.tolerance,
        min_line_length=settings.min_line_length,
    )

    # Analyze
    result = engine.analyze(grid)

    # Count lines by type
    h_lines = sum(
        len(g.lines)
        for g in result.groups_found
        if g.direction == Direction.HORIZONTAL
    )
    v_lines = sum(
        len(g.lines) for g in result.groups_found if g.direction == Direction.VERTICAL
    )

    typer.echo(f"\nDetected Structure:")
    typer.echo(f"  Horizontal lines: {h_lines}")
    typer.echo(f"  Vertical lines: {v_lines}")
    typer.echo(f"  Parallel groups: {len(result.groups_found)}")

    if show_lines:
        typer.echo("\nDetected Lines:")
        for group in result.groups_found:
            for line in group.lines:
                start = line.start_position()
                end = line.end_position()
                typer.echo(
                    f"  - {line.direction.name}: "
                    f"({start.row},{start.col}) to ({end.row},{end.col}) "
                    f"[length={line.length()}]"
                )

    if show_parallel:
        typer.echo("\nParallel Line Groups:")
        for i, group in enumerate(result.groups_found):
            typer.echo(f"  Group {i + 1} ({group.direction.name}):")
            typer.echo(f"    Lines: {len(group.lines)}")
            if group.reference_line:
                ref = group.reference_line
                typer.echo(
                    f"    Reference: row={ref.dominant_row()}, "
                    f"col={ref.dominant_col()}, length={ref.length()}"
                )
            if group.expected_position is not None:
                typer.echo(f"    Expected position: {group.expected_position}")

    if show_issues:
        typer.echo("\nDetected Issues:")
        if result.corrections_count == 0:
            typer.echo("  No alignment issues detected")
        else:
            typer.echo(f"  {result.corrections_count} misaligned lines found:")
            for corr in result.corrections_applied:
                direction = corr.line.direction.name.lower()
                if corr.row_offset != 0:
                    typer.echo(
                        f"    - {direction.capitalize()} line at row "
                        f"{corr.line.dominant_row()} is off by {abs(corr.row_offset)} rows"
                    )
                if corr.col_offset != 0:
                    typer.echo(
                        f"    - {direction.capitalize()} line at col "
                        f"{corr.line.dominant_col()} is off by {abs(corr.col_offset)} cols"
                    )
