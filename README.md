
```
===============================================================================

     _    ____   ____ ___ ___    ____                          _
    / \  / ___| / ___|_ _|_ _|  / ___|___  _ __ _ __ ___  ___| |_ ___  _ __
   / _ \ \___ \| |    | | | |  | |   / _ \| '__| '__/ _ \/ __| __/ _ \| '__|
  / ___ \ ___) | |___ | | | |  | |__| (_) | |  | | |  __/ (__| || (_) | |
 /_/   \_\____/ \____|___|___|  \____\___/|_|  |_|  \___|\___|\__\___/|_|

                          ASCII Diagram Corrector
                               Version 0.1.0

===============================================================================
```

    PRODUCT DESCRIPTION
    -------------------

    ASCII Corrector is a command-line utility for the automatic correction
    of shifted and misaligned lines in ASCII diagrams.  It detects parallel
    line segments, identifies alignment errors, snaps stray characters to
    their nearest structural line, and applies precise corrections to
    restore diagram integrity.

    Operates on plain text files and Markdown documents.  Designed for
    developers, technical writers, and anyone maintaining ASCII art in
    documentation or source code.


    SYSTEM REQUIREMENTS
    -------------------

    Operating System .... Any (Windows, macOS, Linux)
    Python .............. 3.12 or later
    Disk Space .......... Minimal


    INSTALLATION
    ------------

    From source:

        $ git clone <repository-url>
        $ cd AsciDiagramsCorrector
        $ pip install -e .

    For development (includes test and lint tooling):

        $ pip install -e ".[dev]"


    COMMAND REFERENCE
    -----------------

    The tool provides three subcommands:


    CORRECT -- Apply corrections to a diagram file.

        $ ascii-corrector correct <input-file> [options]

        Options:
          -o, --output FILE     Write result to FILE (default: stdout)
          -i, --in-place        Modify the input file directly
          -n, --dry-run         Show corrections without applying them
          -t, --tolerance N     Row/column tolerance (0-5, default: 1)

        Examples:
          $ ascii-corrector correct diagram.txt
          $ ascii-corrector correct diagram.txt -o fixed.txt
          $ ascii-corrector correct diagram.txt --in-place
          $ ascii-corrector correct diagram.txt --dry-run


    ANALYZE -- Inspect a diagram without modifying it.

        $ ascii-corrector analyze <input-file> [options]

        Options:
          -l, --lines           Show all detected lines
          -p, --parallel        Show parallel line groups
          --issues/--no-issues  Show or hide detected issues (default: on)
          -t, --tolerance N     Row/column tolerance (0-5, default: 1)

        Examples:
          $ ascii-corrector analyze diagram.txt
          $ ascii-corrector analyze diagram.txt --lines --parallel


    FIX-MD -- Correct diagrams embedded in Markdown files.

        $ ascii-corrector fix-md [options] <file> [<file> ...]

        Options:
          --no-backup           Skip creating .bak backup file
          -n, --dry-run         Show what would change without applying
          -t, --tolerance N     Row/column tolerance (0-5, default: 1)

        Note: Options must precede file arguments.

        Examples:
          $ ascii-corrector fix-md README.md
          $ ascii-corrector fix-md --no-backup doc1.md doc2.md
          $ ascii-corrector fix-md --dry-run ARCHITECTURE.md


    GENERAL OPTIONS
    ---------------

        -v, --version           Print version number and exit
        -V, --verbose           Enable verbose (debug) output


    HOW IT WORKS
    ------------

    The correction pipeline processes a diagram through six stages:

```
    Input Text
        |
        v
    +-------------------+
    |   Line Detector   |  Scan grid for line characters (- | = + etc.)
    +-------------------+  Group consecutive chars into Line objects.
        |
        v
    +-------------------+
    | Parallel Finder   |  Cluster lines by direction and proximity.
    +-------------------+  Identify groups that should be aligned.
        |
        v
    +-------------------+
    | Alignment Calc.   |  Pick reference line per group.
    +-------------------+  Compute row/column shift offsets.
        |
        v
    +-------------------+
    | Stray Char Finder |  Locate orphan line characters not part of
    +-------------------+  any detected line; snap to nearest match.
        |
        v
    +-------------------+
    | Row Shift Detect. |  Build column histogram of structural chars.
    +-------------------+  Detect and correct whole-row offsets.
        |
        v
    +-------------------+
    | Shift Corrector   |  Apply all corrections to a copy of the grid.
    +-------------------+  Skip any that would exceed grid bounds.
        |
        v
    Corrected Text
```


    CONFIGURATION
    -------------

    All settings may be specified via environment variables with the
    ASCII_CORR_ prefix, or through a .env file in the working directory.

    Variable                        Default     Description
    ------------------------------ ----------- ----------------------------
    ASCII_CORR_TOLERANCE            1           Parallel detection tolerance
    ASCII_CORR_MIN_LINE_LENGTH      2           Minimum chars for a line
    ASCII_CORR_MIN_OVERLAP_RATIO    0.5         Overlap ratio for parallels
    ASCII_CORR_PRESERVE_CONNECTIONS true        Adjust corners on shift
    ASCII_CORR_DRY_RUN              false       Analyze without applying
    ASCII_CORR_LOG_LEVEL            INFO        DEBUG, INFO, WARNING, ERROR
    ASCII_CORR_LOG_FORMAT           json        json or console
    ASCII_CORR_DEFAULT_ENCODING     utf-8       File encoding
    ASCII_CORR_BACKUP_SUFFIX        .bak        Backup file extension


    PROJECT STRUCTURE
    -----------------

```
    src/ascii_corrector/
    |-- domain/            Value objects: Position, Cell, Grid, Line
    |-- detection/         LineDetector, ParallelLineFinder
    |-- correction/        AlignmentCalculator, StrayCharacterFinder,
    |                      RowShiftCorrector, ShiftCorrector,
    |                      CorrectionEngine (orchestrator)
    |-- io/                MarkdownParser, DiagramClassifier,
    |                      MarkdownCorrector, BackupManager
    |-- cli/commands/      Typer subcommands: correct, analyze, fix-md
    |-- config/            Pydantic Settings with env var support
    `-- logging/           structlog setup (JSON / console)

    tests/
    |-- unit/              Fast, isolated tests per module
    |-- integration/       Component interaction tests
    |-- e2e/               Full CLI pipeline tests
    `-- fixtures/          Test data and sample diagrams
```


    DEVELOPMENT
    -----------

    Run the test suite:

        $ pytest                              # all tests
        $ pytest -m unit                      # unit tests only
        $ pytest -m integration               # integration tests only
        $ pytest -m e2e                       # end-to-end tests only
        $ pytest --cov=src --cov-fail-under=80  # with coverage

    Lint and format:

        $ ruff check src tests                # lint
        $ black src tests && isort src tests  # format
        $ mypy src                            # type check
        $ pre-commit run --all-files          # all checks


    EXAMPLE
    -------

    Given a misaligned diagram (note the shifted response arrow):

```
        +----------+         +----------+
        |  Server  |         |  Client  |
        +----------+         +----------+
             |                     |
             |   request           |
             |-------------------->|
             |                     |
             |   response          |
              |<--------------------|
             |                     |
        +----------+         +----------+
        |  Server  |         |  Client  |
        +----------+         +----------+
```

    After running  ascii-corrector correct :

```
        +----------+         +----------+
        |  Server  |         |  Client  |
        +----------+         +----------+
             |                     |
             |   request           |
             |-------------------->|
             |                     |
             |   response          |
             |<--------------------|
             |                     |
        +----------+         +----------+
        |  Server  |         |  Client  |
        +----------+         +----------+
```

    The extra leading space on the response arrow is removed,
    restoring proper vertical alignment.


    LICENSE
    -------

    Released under the MIT License.
    Copyright (c) Andrei Beliak.


```
===============================================================================
    ASCII Corrector 0.1.0                                    Andrei Beliak
===============================================================================
```
