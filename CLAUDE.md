# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install
pip install -e ".[dev]"

# Tests
pytest                                    # All tests
pytest tests/unit/domain/test_position.py -v  # Single file
pytest -m unit                            # Unit only
pytest -m integration                     # Integration only
pytest -m e2e                             # E2E only
pytest --cov=src --cov-fail-under=80      # With coverage

# Lint & format
ruff check src tests                      # Lint
black src tests && isort src tests        # Format
mypy src                                  # Type check
pre-commit run --all-files                # All checks

# CLI
ascii-corrector correct input.txt -o output.txt
ascii-corrector analyze input.txt
ascii-corrector fix-md README.md --no-backup
```

## Architecture

Python 3.12 CLI tool using Typer. Corrects shifted/misaligned lines in ASCII diagrams.

### Correction Pipeline

`CorrectionEngine` orchestrates: `LineDetector` → `ParallelLineFinder` → `AlignmentCalculator` → `StrayCharacterFinder` → `RowShiftCorrector` → `ShiftCorrector`.

1. **Detection**: Scan `Grid` for line characters (`-`, `|`, `=`, `+`, etc.), group consecutive chars into `Line` objects
2. **Parallel Finding**: Group lines by direction, cluster by position within tolerance, check overlap
3. **Alignment**: For each `ParallelGroup`, pick a reference line and compute `ShiftCorrection` offsets
4. **Stray Character Finding**: Find individual line chars (`|`, `!`, `-`, `=`, `_`) not part of any detected line and produce corrections to snap them to the nearest detected line of matching direction. Skips strays on rows/columns containing text to avoid breaking formatting (exception: right-edge pipes).
5. **Row Shift Detection**: Use column consensus — build a histogram of structural chars (`|`, `+`, `!`) per column, then detect rows where all structural chars are offset from a more-popular nearby column. Produces whole-row shift corrections.
6. **Correction**: Apply all `ShiftCorrection`s to a copied `Grid`, skip any that would go out of bounds

**Correction scope**: The engine aligns lines that are the same direction, within `tolerance` rows/columns of each other, AND have overlapping column/row ranges.

**Advanced Features**:
- **Box Detection** (`BoxDetector`): Explicitly detects rectangular structures, handles large boxes where top/bottom are far apart
- **Structure Classification** (`StructureClassifier`): Identifies diagram types (BOX, TREE, GRAPH), preserves tree branches without correction
- **Character Constants** (`character_constants.py`): Comprehensive Unicode support (light/heavy/double boxes, corners, junctions, diagonals)
- **Diagonal Support**: Detects and corrects diagonal lines (/, \, ╱, ╲)

### Key Types

- **`Grid`** (`domain/grid.py`): Mutable 2D char matrix. `Grid.from_string(text)` / `grid.to_string()`. Central data structure.
- **`Line`** (`domain/line.py`): List of `Cell`s with a `Direction`. Has `dominant_row()`/`dominant_col()` for alignment.
- **`CorrectionResult`** (`correction/protocols.py`): Holds original grid, corrected grid, applied corrections, groups found.
- **`ParallelGroup`** (`detection/protocols.py`): Group of lines that should be aligned.

### Module Layout

- **`domain/`**: Value objects (`Position`, `Character`, `Cell`, `Grid`, `Line`). Character classification via frozensets in `character_constants.py`. Includes `CharacterClass` enum with ASCII/Unicode/Diagonal support.
- **`detection/`**: `LineDetector` scans grid; `ParallelLineFinder` clusters lines; `BoxDetector` detects rectangular structures; `StructureClassifier` identifies diagram types (BOX, TREE, GRAPH).
- **`correction/`**: `AlignmentCalculator` computes offsets; `StrayCharacterFinder` snaps orphan chars to nearby lines; `RowShiftCorrector` fixes whole-row horizontal shifts via column consensus; `BoxAlignmentCalculator` aligns box edges; `ShiftCorrector` applies all corrections; `CorrectionEngine` orchestrates.
- **`io/`**: Markdown processing — `MarkdownParser` extracts fenced code blocks, `DiagramClassifier` identifies diagram content by language label + char ratio, `MarkdownCorrector` orchestrates per-block correction, `BackupManager` creates `.bak` files.
- **`cli/commands/`**: Typer subcommands (`correct`, `analyze`, `fix-md`). Each file creates a `typer.Typer()` app registered in `cli/app.py`.
- **`config/`**: Pydantic `Settings` with `ASCII_CORR_` env prefix.
- **`logging/`**: structlog setup (JSON or console format).

### Protocols

Each layer defines `protocols.py` with `@runtime_checkable Protocol` classes as interfaces. Implementations are separate files.

## Development Conventions

- **TDD**: Write failing test first, then implement, then refactor. Test file goes in `tests/unit/<module>/test_<feature>.py`.
- **New feature pattern**: Test → Protocol in `protocols.py` → Implementation → Integration test.
- **Dataclasses**: Use `frozen=True` for value objects, mutable for aggregates like `Grid`.
- **Config**: All settings via `ASCII_CORR_` env vars or `.env` file. See `config/settings.py` for full list.
- **CLI note**: Typer variadic arguments (`list[Path]`) require options to come **before** the file arguments (e.g., `fix-md --no-backup file.md`). This is due to the callback pattern used for command groups. Tests validate this behavior; see `tests/e2e/test_cli_*.py` for examples.
- **Ruff exceptions**: `B008` and `ARG001` warnings on Typer commands are expected (Typer's API requires default function calls and `ctx` parameter).
- **Latest Updates**: Fixed 10 failing E2E tests (commit 3b24274) - CLI now properly handles all argument orders with clear validation.
