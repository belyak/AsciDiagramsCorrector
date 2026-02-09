# ASCII Diagram Corrector - Advanced Features

This document describes the four major features that enable robust correction of diverse ASCII diagram patterns.

## Overview

The ASCII Diagram Corrector handles four categories of edge cases that would otherwise cause traditional parallel-line detection to fail:

1. **Unicode Box-Drawing Characters** - Comprehensive support for Unicode box elements
2. **Large Box Detection** - Explicit box structure detection for boxes larger than tolerance
3. **Tree Structure Preservation** - Pattern recognition to preserve tree diagrams
4. **Diagonal Line Support** - Detection and correction of diagonal connections

---

## Feature 1: Unicode Box-Drawing Character Support

### Problem

ASCII diagrams often use box-drawing characters for improved visual appearance. Traditional implementations only recognize ASCII characters (`-`, `|`, `+`), causing Unicode elements to be ignored or misclassified.

### Solution

Complete character classification system supporting Unicode box-drawing characters across all stages of the correction pipeline.

### Supported Characters

#### ASCII Characters (Original)
```
Horizontal:  -  =  _
Vertical:    |  !
Corners:     +  .  '  `
Junctions:   *
```

#### Unicode Single-Line
```
Horizontal:  ─ (U+2500)
Vertical:    │ (U+2502)
Corners:     ┌ ┐ └ ┘
Junctions:   ├ ┤ ┬ ┴ ┼
```

#### Unicode Heavy-Line
```
Horizontal:  ━ (U+2501)
Vertical:    ┃ (U+2503)
Corners:     ┏ ┓ ┗ ┛
Junctions:   ┠ ┨ ┯ ┷ ┿ ╋
```

#### Unicode Double-Line
```
Horizontal:  ═ (U+2550)
Vertical:    ║ (U+2551)
Corners:     ╔ ╗ ╚ ╝
Junctions:   ╠ ╣ ╦ ╩ ╬
```

### Example

**Input (Unicode box with misaligned bottom):**
```
┌──────────┐
│ Process  │
 └─────────┘
```

**After Correction:**
```
┌──────────┐
│ Process  │
└──────────┘
```

### Implementation Details

- **Module**: `src/ascii_corrector/domain/character_constants.py`
- **Character Classification**: `character.py` uses frozensets for O(1) lookup
- **Coverage**: All detection and correction stages recognize Unicode characters
- **Test Coverage**: 17+ tests covering all character classes

### CLI Usage

```bash
# Unicode diagrams are processed transparently
$ ascii-corrector correct diagram_unicode.txt
$ ascii-corrector analyze diagram_unicode.txt --lines
```

---

## Feature 2: Large Box Detection

### Problem

The default parallel-line algorithm groups lines by proximity (within `tolerance` rows/columns). Boxes where top and bottom edges are separated by many rows form separate line groups that cannot be aligned together, preventing correction of misaligned edges.

**Example:**
```
+----------+
|          |    <- Top and bottom edges are 5 rows apart
|          |    <- Default tolerance is 1, so they form separate groups
|          |
|          |
 +--------+    <- Misaligned - won't be corrected
```

### Solution

Explicit box structure detection that identifies rectangular patterns and enforces alignment of all four edges as a unit.

### Algorithm

1. **Corner Detection**: Scan grid for corner characters (`+`, `.`, `┌`, etc.)
2. **Edge Tracing**: From each corner, trace horizontally and vertically to find edges
3. **Validation**: Confirm all four corners exist and form a valid rectangle
4. **Alignment**: Calculate corrections to align all edges with the reference lines

### Features

- Handles any box size (1x1 to full grid)
- Preserves box integrity during alignment
- Works with both ASCII and Unicode corners
- Respects tolerance setting for edge alignment

### Example

**Input (Large misaligned box):**
```
+------+
|      |
|      |
|      |
|      |
 +-----+
```

**After Correction:**
```
+------+
|      |
|      |
|      |
|      |
+------+
```

### Implementation Details

- **Module**: `src/ascii_corrector/detection/box_detector.py`
- **Alignment**: `src/ascii_corrector/correction/box_alignment_calculator.py`
- **Pipeline Integration**: BoxDetector runs before parallel line detection in `CorrectionEngine`
- **Test Coverage**: 20+ tests covering box detection and alignment

### CLI Usage

```bash
$ ascii-corrector correct large_diagram.txt --dry-run
$ ascii-corrector analyze complex_diagram.txt  # Shows detected boxes
```

---

## Feature 3: Tree Structure Preservation

### Problem

Tree diagrams use branch notation (e.g., `+--`, `├──`) that can be misidentified as horizontal line segments by the parallel-line detector, resulting in unwanted "corrections".

**Example:**
```
root
 |
 +-- branch1
 +-- branch2

# Without preservation, the '+' might be treated as a box corner
# and the '+-' might be treated as a misaligned horizontal line
```

### Solution

Structure classification that identifies tree patterns and skips correction when tree structures are detected.

### Classification Logic

The `StructureClassifier` uses pattern recognition to identify:

1. **Tree Patterns**: Presence of vertical lines (`|`) with branch notation (`+--`)
2. **Tree Indicators**:
   - Indented branch segments
   - Consistent vertical alignment of trunk
   - Branch segments extending horizontally from trunk

3. **Exclusion**: Distinguishes trees from boxes by checking for:
   - Closed rectangles (indicates box, not tree)
   - Multiple branching points
   - Leaf nodes or terminal markers

### Example

**Input (Tree diagram - no correction applied):**
```
                Organization
                     |
            +--------+--------+
            |                 |
         Sales           Engineering
            |                 |
       +----+----+        +---+---+
       |         |        |       |
      East     West    Frontend Backend
```

**Output (Unchanged - structure preserved):**
```
                Organization
                     |
            +--------+--------+
            |                 |
         Sales           Engineering
            |                 |
       +----+----+        +---+---+
       |         |        |       |
      East     West    Frontend Backend
```

### Configuration

```bash
# Enable tree preservation (default: true)
$ export ASCII_CORR_PRESERVE_TREES=true
$ ascii-corrector correct diagram.txt

# Disable to apply corrections even on trees
$ export ASCII_CORR_PRESERVE_TREES=false
$ ascii-corrector correct diagram.txt
```

### Implementation Details

- **Module**: `src/ascii_corrector/detection/structure_classifier.py`
- **Integration**: `CorrectionEngine` checks structure type before applying corrections
- **Setting**: `preserve_trees` in `config/settings.py`
- **Test Coverage**: 10+ tests covering tree detection and preservation

---

## Feature 4: Diagonal Line Support

### Problem

Diagonal connections in diagrams provide visual flow between non-aligned elements. Without explicit support, diagonal characters are ignored or treated as noise.

### Solution

Full support for diagonal line detection and correction alongside horizontal and vertical lines.

### Supported Characters

#### ASCII Diagonal
```
Down (\): backslash (U+005C)
Up (/):   forward slash (U+002F)
```

#### Unicode Diagonal
```
Down (\): ╲ BOX DRAWINGS LIGHT DIAGONAL (U+2572)
Up (/):   ╱ BOX DRAWINGS LIGHT DIAGONAL (U+2571)
```

### Directions

The `Direction` enum includes:
```python
HORIZONTAL   # Rows of the same y-coordinate
VERTICAL     # Columns of the same x-coordinate
DIAGONAL_DOWN # Top-left to bottom-right (\)
DIAGONAL_UP   # Bottom-left to top-right (/)
```

### Examples

**Input (Misaligned diagonals):**
```
A
 \
  \
  B
```

**After Correction:**
```
A
 \
  \
   B
```

**Complex diagonal network:**
```
    A
   / \
  B   C
   \ /
    D
```

### Detection Algorithm

1. **Character Scanning**: Identify diagonal characters in grid
2. **Line Grouping**: Consecutive diagonal characters with correct slope form a line
3. **Direction Detection**: Determine if line is DIAGONAL_UP or DIAGONAL_DOWN
4. **Alignment**: Check alignment with other diagonals in same direction
5. **Correction**: Apply shift corrections for misaligned diagonals

### Implementation Details

- **Character Classes**: `DIAGONAL_DOWN`, `DIAGONAL_UP` in `CharacterClass` enum
- **Detection**: `LineDetector` extends scanning to detect diagonal patterns
- **Module**: `src/ascii_corrector/detection/line_detector.py`
- **Test Coverage**: 15+ tests for diagonal detection and correction

### CLI Usage

```bash
# Diagonals are handled transparently
$ ascii-corrector correct flow_diagram.txt
$ ascii-corrector analyze diagram.txt --lines  # Shows detected diagonals
```

---

## Integration in Correction Pipeline

All four features are integrated into the main correction pipeline:

```
Input Grid
    |
    v
[Unicode Character Recognition] <- Feature 1: Unicode Support
    |
    v
[Structure Classification] <- Feature 3: Tree Detection
    |
    +-> If tree: Skip corrections and return unchanged
    |
    v
[Box Detection] <- Feature 2: Large Box Detection
    |
    v
[Line Detection] <- Feature 4: Diagonal Support
    |
    v
[Parallel Line Finding]
    |
    v
[Alignment Calculation]
    |
    v
[Stray Character Snapping]
    |
    v
[Row Shift Detection]
    |
    v
[Correction Application]
    |
    v
Output Grid
```

---

## Testing

### Test Coverage

- **Unit Tests**: 17+ Unicode, 20+ Box, 10+ Tree, 15+ Diagonal tests
- **Integration Tests**: Box + Tree interaction, Unicode in all contexts
- **E2E Tests**: Real diagrams with mixed features
- **Fixtures**: 29+ test diagram files covering all features

### Running Feature Tests

```bash
# All feature tests
$ pytest tests/unit/detection/test_box_detector.py
$ pytest tests/unit/detection/test_structure_classifier.py
$ pytest tests/unit/detection/test_diagonal_detection.py
$ pytest tests/unit/domain/test_character.py

# Integration tests
$ pytest tests/e2e/test_box_and_tree_integration.py

# Test specific feature
$ pytest tests/ -k "unicode"
$ pytest tests/ -k "diagonal"
$ pytest tests/ -k "tree"
```

---

## Performance

All features maintain excellent performance:

- **Unicode Support**: Same O(1) character lookup as ASCII
- **Box Detection**: O(n*m) grid scan, minimal overhead
- **Tree Classification**: Pattern matching on detected structures
- **Diagonal Detection**: Same linear scan as other line types
- **Overall**: < 100ms for typical diagrams (< 50 rows × 100 cols)

---

## Backward Compatibility

All features are fully backward compatible:

- **ASCII-Only Diagrams**: Work exactly as before
- **Mixed ASCII/Unicode**: Transparently supported
- **Configuration**: All features are enabled by default
- **CLI**: No changes to command-line interface

---

## Future Enhancements

Potential areas for expansion:

1. **Curved Connectors**: Support for arc-shaped connections
2. **Advanced Tree Styles**: Different branch notations (e.g., `<--`, `-->`)
3. **3D Diagrams**: Support for 3D perspective drawings
4. **Anti-Aliasing**: Smoothing of diagonal edges
5. **Custom Character Sets**: User-defined diagram character libraries

---

## Related Documentation

- **README.md**: User-facing feature overview
- **CLAUDE.md**: Developer architecture and guidelines
- **ARCHITECTURE.md**: Detailed technical architecture
- **DEVELOPMENT_EFFORT_REPORT.md**: Implementation history and metrics
