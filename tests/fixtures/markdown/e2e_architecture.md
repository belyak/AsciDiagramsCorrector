# ASCII Diagram Corrector — Architecture

This document serves as an end-to-end test for the correction tool. It contains
well-formed diagrams, intentionally broken diagrams, and non-diagram code blocks.

## 1. Package Dependency Graph (well-formed — should be untouched)

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

## 2. Python Code (non-diagram — should be skipped entirely)

```python
class CorrectionEngine:
    def __init__(self, tolerance=1):
        self._tolerance = tolerance

    def correct(self, grid: Grid) -> CorrectionResult:
        lines = self._detector.detect_lines(grid)
        groups = self._finder.find_parallel_groups(lines)
        return self._apply(groups, grid)
```

## 3. Correction Pipeline (well-formed — should be untouched)

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
```

## 4. Shifted Parallel Lines (BROKEN — should be corrected)

These are parallel lines where one is shifted by a row. The correction
engine should align them.

```
----------
 ----------
----------
 ----------
```

## 5. Domain Model Relationships (well-formed — should be untouched)

```
 +------------------+         +-----------------+
 | CharacterClass   |         |   Direction     |
 | (Enum)           |         |   (Enum)        |
 |                  |         |                 |
 | HORIZONTAL       |         | HORIZONTAL      |
 | VERTICAL         |         | VERTICAL        |
 +------------------+         +-----------------+
```

## 6. JavaScript Code (non-diagram — should be skipped)

```javascript
function analyzeGrid(grid) {
    const lines = detectLines(grid);
    const groups = findParallelGroups(lines);
    return calculateCorrections(groups);
}
```

## 7. Shifted Horizontal Segments (BROKEN — should be corrected)

Adjacent horizontal lines that should be aligned:

```
========
 ========
========
```

## 8. Exception Hierarchy (well-formed — should be untouched)

```
+------------------------------------------+
|           AsciiCorrectorError            |
+------------------------------------------+
|                                          |
|  DiagramParseError                       |
|  InvalidGridError                        |
|  LineDetectionError                      |
|  CorrectionError                         |
|    CollisionError                        |
|    BoundsError                           |
|  ConfigurationError                      |
|  DiagramIOError                          |
|  MarkdownParseError                      |
|  BackupError                             |
|                                          |
+------------------------------------------+
```

## 9. CLI Command Routing (well-formed — should be untouched)

```
  ascii-corrector
       |
       +-- main callback
       |
       +--[ correct ]
       |
       +--[ analyze ]
       |
       +--[ fix-md ]
```

## 10. Settings Layout (well-formed — should be untouched)

```
+--------------------------------------------------------------+
| Settings (pydantic BaseSettings)                             |
| env_prefix = "ASCII_CORR_"                                  |
|--------------------------------------------------------------|
| tolerance: 1   | log_level: INFO   | encoding: utf-8        |
| min_line: 2    | log_format: json  | diagram_languages: ... |
| min_overlap: .5| dry_run: False    | min_char_ratio: 0.05   |
+--------------------------------------------------------------+
```

## 11. More Shifted Lines (BROKEN — should be corrected)

```
-----
 -----
```

## 12. Mixed Well-formed Boxes (well-formed — should be untouched)

```
+-------+    +-------+    +-------+
| Grid  |    | Line  |    | Cell  |
+-------+    +-------+    +-------+
```

## 13. Markdown Correction Data Flow (well-formed — should be untouched)

```
+------------------+     +-------------------+     +-------------------+
| Input .md file   |---->| MarkdownParser    |---->| DiagramClassifier |
|                  |     | parse(text)       |     | is_diagram()      |
+------------------+     +-------------------+     +-------------------+
                                                              |
                                                              v
+------------------+     +-------------------+     +-------------------+
| Output .md file  |<----| MarkdownDocument  |<----| CorrectionEngine  |
| (corrected)      |     | .replace_content()|     | .correct(grid)    |
+------------------+     +-------------------+     +-------------------+
```

## 14. Shell Commands (non-diagram — should be skipped)

```bash
pytest tests/unit/io/ -v
ascii-corrector fix-md docs/ARCHITECTURE.md --dry-run
ruff check src tests
```

## 15. Shifted Underscores (BROKEN — should be corrected)

```
____
 ____
____
 ____
```
