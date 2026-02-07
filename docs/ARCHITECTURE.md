# ASCII Diagram Corrector — Architecture

High-level architecture of the project, illustrated with ASCII diagrams.

## 1. Package Dependency Graph

Shows how the six main packages depend on each other. Arrows indicate import direction.

```
+-------------+     +-------------+     +-----------+
|   domain    |<----| detection   |<----|           |
| (core types)|     | (line scan) |     |           |
+-------------+     +-------------+     |           |
      ^                    ^            |correction |
      |                    |            | (engine)  |
      +--------------------+----------->|           |
                                        +-----------+
                                              ^
                                              |
+-------------+     +-------------+     +-----------+
|   config    |<----|    cli      |---->|    io     |
| (settings)  |     | (commands)  |     | (markdown)|
+-------------+     +-------------+     +-----------+
                          |
                    +-----v-------+
                    |   logging   |
                    | (structlog) |
                    +-------------+
```

## 2. Correction Pipeline

The core algorithm flows through four stages. `CorrectionEngine` orchestrates the full pipeline.

```
+------------------+      +---------------------+      +----------------------+      +------------------+
|   LineDetector   |----->| ParallelLineFinder  |----->| AlignmentCalculator  |----->|  ShiftCorrector  |
|                  |      |                     |      |                      |      |                  |
| Scans Grid for   |      | Groups lines by     |      | Picks reference line |      | Clears old cells |
| horizontal and   |      | direction, clusters |      | per group, computes  |      | places chars at  |
| vertical lines   |      | by position within  |      | row/col offsets for  |      | new positions on |
|                  |      | tolerance, checks   |      | each misaligned line |      | a copied Grid    |
|                  |      | overlap ratio       |      |                      |      |                  |
+------------------+      +---------------------+      +----------------------+      +------------------+

 Input: Grid              Output: list[Line]          Output: list[ParallelGroup]    Output: CorrectionResult
        |                         |                           |                              |
        v                         v                           v                              v
  Grid.from_string()    detect_lines(grid)      find_parallel_groups(lines)      correct(grid) / analyze(grid)
```

## 3. Domain Model Relationships

Value objects use `frozen=True` dataclasses. `Grid` is the only mutable aggregate.

```
 +------------------+         +-----------------+
 | CharacterClass   |         |   Direction     |
 | (Enum)           |         |   (Enum)        |
 |                  |         |                 |
 | HORIZONTAL       |         | HORIZONTAL      |
 | VERTICAL         |         | VERTICAL        |
 | CORNER           |         | DIAGONAL_DOWN   |
 | JUNCTION         |         | DIAGONAL_UP     |
 | ARROW            |         |                 |
 | TEXT             |         +-----------------+
 | WHITESPACE       |               |
 | UNKNOWN          |               |
 +------------------+               |
        ^                           |
        | char_class                |
 +------+----------+                |
 | Character       |                |
 | (frozen)        |                |
 |                 |                |
 | value: str      |                |
 | is_line_char()  |                |
 | is_corner()     |                |
 | is_junction()   |                |
 +--------+--------+                |
          |                         |
          v  has-a                  v  has-a
 +--------+--------+    +-----------+------+
 |     Cell        |    |      Line        |
 |   (frozen)      |    |   (mutable)      |
 |                 |    |                  |
 | character: Char |    | cells: list[Cell]|
 | position: Pos   |    | direction: Dir   |
 | is_empty()      |    | dominant_row()   |
 | is_structural() |    | dominant_col()   |
 +--------+--------+    | start_position() |
          ^             | end_position()   |
          |             | length()         |
          | creates     +------------------+
          |
 +--------+--------+
 |     Grid        |
 | (mutable)       |
 |                 |
 | _data: str[][]  |
 | width, height   |
 | from_string()   |
 | to_string()     |
 | get_cell()      |
 | set_cell()      |
 | copy()          |
 +-----------------+

 +------------------+
 | Position         |
 | (frozen)         |
 |                  |
 | row: int         |
 | col: int         |
 | offset()         |
 | distance_to()    |
 | manhattan_dist() |
 +------------------+
```

## 4. Exception Hierarchy

Custom exceptions with contextual metadata.

```
 Exception
   |
   +-- AsciiCorrectorError(message, **context)
         |
         +-- DiagramParseError
         |
         +-- InvalidGridError
         |
         +-- LineDetectionError
         |
         +-- CorrectionError
         |     |
         |     +-- CollisionError
         |     |
         |     +-- BoundsError
         |
         +-- ConfigurationError
         |
         +-- DiagramIOError
         |
         +-- MarkdownParseError
         |
         +-- BackupError
```

## 5. CLI Command Routing

Typer app with three registered subcommands.

```
  ascii-corrector
       |
       +-- main callback (--version, --verbose)
       |
       +--[ correct ]------+---> Reads file
       |   -o, -i, -n, -t  |     Grid.from_string()
       |                   |     CorrectionEngine.correct()
       |                   +---> Writes to file/stdout
       |
       +--[ analyze ]------+---> Reads file
       |   -l, -p, -t      |     Grid.from_string()
       |   --issues        |     CorrectionEngine.analyze()
       |                   +---> Prints report
       |
       +--[ fix-md ]-------+---> Reads .md files
           --no-backup     |     MarkdownParser.parse()
           -n, -t          |     DiagramClassifier.is_diagram()
                           |     CorrectionEngine.correct() per block
                           |     BackupManager.create_backup()
                           +---> Writes corrected .md in-place
```

## 6. Markdown Correction Flow

The `fix-md` command processes Markdown files containing embedded diagrams.

```
 +------------------+     +-------------------+     +-------------------+
 | Input .md file   |---->| MarkdownParser    |---->| DiagramClassifier |
 |                  |     |                   |     |                   |
 | # Title          |     | parse(text)       |     | is_diagram()      |
 | ```              |     | -> MarkdownDoc    |     | language check    |
 | +--+             |     |   with CodeBlocks |     | + char ratio      |
 | |  |             |     |                   |     |                   |
 | +--+             |     +-------------------+     +---------+---------+
 | ```              |                                         |
 | more text        |                               diagram blocks only
 +------------------+                                         |
                                                              v
 +------------------+     +-------------------+     +---------+---------+
 | Output .md file  |<----| MarkdownDocument  |<----| CorrectionEngine  |
 | (corrected)      |     | .replace_content()|     |                   |
 +------------------+     | (reverse order)   |     | Grid.from_string()|
                          +-------------------+     | .correct(grid)    |
         +-------------------+                      | .to_string()      |
         | BackupManager     |                      +-------------------+
         | .create_backup()  |
         | file.md.bak       |
         +-------------------+
```

## 7. Detection Algorithm Detail

How `LineDetector` scans a grid, row by row and column by column.

```
  Horizontal Scan (row by row):              Vertical Scan (col by col):

  Row 0: + - - - - +    detected: "----"     Col 0: +    detected: "|"
  Row 1: |         |    (skip non-line)             |    (vertical)
  Row 2: |         |                                |
  Row 3: + - - - - +    detected: "----"            +

  Result:                                    Col 5: +    detected: "|"
  Line(cells=[...], dir=HORIZONTAL)                 |    (vertical)
  at rows 0 and 3                                   |
                                                    +

  Then ParallelLineFinder groups:
  +----------------------------------------------+
  | ParallelGroup                                |
  | direction: HORIZONTAL                        |
  | lines: [line_row0, line_row3]                |
  | reference: line_row0 (longest)               |
  | expected_position: row 0                     |
  +----------------------------------------------+
```

## 8. Correction Data Structures

The data types flowing through the correction pipeline.

```
 ShiftCorrection                AlignmentResult                CorrectionResult
 +-------------------+          +---------------------+         +---------------------+
 | line: Line        |   many   | group: ParallelGroup|   many  | original_grid: Grid |
 | row_offset: int   +--------->| corrections: list   +-------->| corrected_grid: Grid|
 | col_offset: int   |          | reference_pos: int  |         | corrections_applied |
 | confidence: float |          +---------------------+         | groups_found        |
 +-------------------+                                          | corrections_count   |
                                                                +---------------------+
```

## 9. Protocol Layer

Each processing layer defines protocols as structural interfaces.

```
  Detection Protocols               Correction Protocols
  +---------------------------+     +---------------------------+
  |                           |     |                           |
  | CharacterClassifierProto  |     | AlignmentCalculatorProto  |
  | classify(char) -> Class   |     | calculate_alignment(grp)  |
  |                           |     |   -> AlignmentResult      |
  | LineDetectorProto         |     |                           |
  | detect_lines(grid)        |     | ShiftCorrectorProto       |
  |   -> list[Line]           |     | apply_correction(corr,    |
  |                           |     |   grid) -> Grid           |
  | ParallelFinderProto       |     |                           |
  | find_parallel_groups(     |     | CorrectionEngineProto     |
  |   lines) -> list[Group]   |     | correct(grid)             |
  |                           |     |   -> CorrectionResult     |
  +---------------------------+     +---------------------------+
```

## 10. Settings Configuration

All settings follow 12-factor principles with environment variable overrides.

```
 +--------------------------------------------------------------+
 | Settings (pydantic BaseSettings)                             |
 | env_prefix = "ASCII_CORR_"                                   |
 |--------------------------------------------------------------|
 | Detection       | Correction     | Logging    | I/O          |
 |-----------------|----------------|------------|--------------|
 | tolerance: 1    | preserve_      | log_level: | encoding:    |
 | min_line_len: 2 |  connections:  |  "INFO"    |  "utf-8"     |
 | min_overlap:    |  True          | log_format:|              |
 |  0.5            | dry_run: False |  "json"    |              |
 |-----------------|----------------|------------|--------------|
 | Markdown                                                     |
 |--------------------------------------------------------------|
 | diagram_languages: ["", "ascii", "text", "diagram", "art"]   |
 | min_diagram_char_ratio: 0.05                                 |
 | backup_suffix: ".bak"                                        |
 +--------------------------------------------------------------+
```
