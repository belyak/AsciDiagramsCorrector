# ASCII Diagram Corrector

A Python CLI tool that uses algorithms to correct ASCII diagrams, focusing on parallel line alignment issues.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Correct a diagram
ascii-corrector correct input.txt -o output.txt

# Analyze a diagram
ascii-corrector analyze input.txt

# Dry run
ascii-corrector correct input.txt --dry-run
```

## Development

```bash
# Run tests
pytest

# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## License

MIT
