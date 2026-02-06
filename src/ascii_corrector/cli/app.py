"""Main CLI application using Typer."""

from typing import Optional

import typer

from ascii_corrector import __version__
from ascii_corrector.cli.commands import analyze, correct, fix_md
from ascii_corrector.config import Settings
from ascii_corrector.logging import configure_logging

app = typer.Typer(
    name="ascii-corrector",
    help="Correct shifted lines in ASCII diagrams using algorithms.",
    add_completion=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"ascii-corrector version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        help="Enable verbose output.",
    ),
) -> None:
    """ASCII Diagram Corrector - Fix shifted parallel lines in ASCII diagrams."""
    settings = Settings()
    log_level = "DEBUG" if verbose else settings.log_level
    log_format = "console" if verbose else settings.log_format
    configure_logging(log_level=log_level, log_format=log_format)


# Register commands
app.add_typer(correct.app, name="correct")
app.add_typer(analyze.app, name="analyze")
app.add_typer(fix_md.app, name="fix-md")


if __name__ == "__main__":
    app()
