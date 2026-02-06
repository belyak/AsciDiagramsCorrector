# ASCII Diagram Corrector

A Python CLI tool that uses algorithms to correct ASCII diagrams, focusing on parallel line alignment issues.

## Project Overview

This tool corrects common issues in AI-generated ASCII diagrams:
- Shifted/misaligned parallel lines
- Missing or incorrect corner characters
- Broken connections between boxes
- Inconsistent line characters

## Architecture

```
src/ascii_corrector/
├── domain/          # Core business objects (Position, Character, Cell, Grid, Line, Diagram)
├── detection/       # Line detection algorithms (CharacterClassifier, LineDetector, ParallelLineFinder)
├── correction/      # Correction algorithms (AlignmentCalculator, ShiftCorrector, CorrectionEngine)
├── io/              # Input/Output (DiagramReader, DiagramWriter)
├── config/          # 12-factor configuration (Pydantic Settings)
├── cli/             # Typer CLI commands (correct, analyze)
└── logging/         # Structured logging (structlog)
```

## Development Guidelines

### TDD (Test-Driven Development)
1. **RED**: Write a failing test first
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Improve while tests pass

```bash
# Run specific test
pytest tests/unit/domain/test_position.py -v

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### OOP Design Principles
- Use classes with single responsibility
- Define protocols (interfaces) in `protocols.py` files
- Prefer composition over inheritance
- Use dataclasses for value objects (frozen=True for immutability)

### 12-Factor App Compliance
- **Config**: Use environment variables with `ASCII_CORR_` prefix
- **Dependencies**: All declared in `pyproject.toml`
- **Logs**: Use structlog, output to stdout in JSON format
- **Processes**: Stateless CLI, no local file state

### Code Style (Strict PEP8)
```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint
ruff check src tests

# Type check
mypy src

# Run all checks
pre-commit run --all-files
```

## Common Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run the CLI
ascii-corrector correct input.txt -o output.txt
ascii-corrector analyze input.txt --verbose
ascii-corrector correct input.txt --dry-run

# Run tests
pytest                                    # All tests
pytest -m unit                            # Unit tests only
pytest -m integration                     # Integration tests only
pytest --cov=src --cov-fail-under=80     # With coverage check
```

## Testing with Claude Code

Generate test diagrams using Claude Code CLI:

```bash
# Generate a broken diagram
claude -p "Create an ASCII box diagram with intentionally shifted lines" > broken.txt

# Correct it
ascii-corrector correct broken.txt -o fixed.txt

# Compare
diff broken.txt fixed.txt
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ASCII_CORR_TOLERANCE` | Row/column tolerance for parallel detection | `1` |
| `ASCII_CORR_MIN_LINE_LENGTH` | Minimum characters to consider a line | `2` |
| `ASCII_CORR_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `ASCII_CORR_LOG_FORMAT` | Log format (json, console) | `json` |

## Key Algorithms

### Line Detection
1. Scan grid for line characters (-, |, =, +)
2. Group consecutive characters into line segments
3. Classify lines by direction (horizontal/vertical)

### Parallel Line Finding
1. Group lines by direction
2. Cluster by position using tolerance
3. Check overlap to confirm parallelism

### Shift Correction
1. For each parallel group, find reference line
2. Calculate offset for each misaligned line
3. Validate no collisions
4. Apply shifts, update grid

## File Organization for New Features

When adding a new feature:

1. **Test first**: Create `tests/unit/<module>/test_<feature>.py`
2. **Protocol**: Define interface in `<module>/protocols.py`
3. **Implementation**: Create `<module>/<feature>.py`
4. **Integration test**: Add to `tests/integration/`
