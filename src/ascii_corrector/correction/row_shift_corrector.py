"""Row shift corrector using column consensus to detect and fix whole-row shifts."""

from collections import defaultdict

from ascii_corrector.correction.protocols import ShiftCorrection
from ascii_corrector.domain import Cell, Direction, Grid, Line, Position
from ascii_corrector.domain.character_constants import CORNER_CHARS, VERTICAL_CHARS


class RowShiftCorrector:
    """
    Detects entire rows that are shifted horizontally and produces
    corrections to realign them.

    Uses a column consensus algorithm:
    1. Build a histogram of how many rows have a structural character
       (``|``, ``+``, ``!``) at each column.
    2. For each row, check whether ALL its structural chars are at columns
       that have a *strictly more popular* neighbour within ``tolerance``.
    3. Verify the target column has a structural char on an adjacent row
       (``row ± 1``), ensuring the corrected char connects to an existing
       vertical structure.
    4. If every structural char on a row would move to the same offset
       ``d``, produce a ShiftCorrection that moves ALL non-space cells
       on that row by ``-d``.
    """

    def __init__(self, tolerance: int = 1, min_consensus: int = 2) -> None:
        self._tolerance = tolerance
        self._min_consensus = min_consensus

    def find_row_shift_corrections(self, grid: Grid) -> list[ShiftCorrection]:
        """
        Scan the grid for rows that are shifted by a consistent column offset.

        Args:
            grid: The grid to scan.

        Returns:
            List of ShiftCorrection objects, one per shifted row.
        """
        if grid.width == 0 or grid.height == 0:
            return []

        # Step 1: Build column histogram and position set of structural chars
        col_counts: dict[int, int] = defaultdict(int)
        structural_positions: set[tuple[int, int]] = set()
        for row in range(grid.height):
            for col in range(grid.width):
                cell = grid.get_cell(Position(row=row, col=col))
                if cell is not None and cell.character.value in (VERTICAL_CHARS | CORNER_CHARS):
                    col_counts[col] += 1
                    structural_positions.add((row, col))

        if not col_counts:
            return []

        # Step 2: For each row, check if structural chars are consistently shifted
        corrections: list[ShiftCorrection] = []
        for row in range(grid.height):
            correction = self._check_row(
                grid, row, col_counts, structural_positions
            )
            if correction is not None:
                corrections.append(correction)

        return corrections

    def _check_row(
        self,
        grid: Grid,
        row: int,
        col_counts: dict[int, int],
        structural_positions: set[tuple[int, int]],
    ) -> ShiftCorrection | None:
        """Check if a single row is consistently shifted from consensus columns."""
        # Collect structural char positions on this row
        row_structural: list[int] = []
        for col in range(grid.width):
            if (row, col) in structural_positions:
                row_structural.append(col)

        if not row_structural:
            return None

        # Compute offset for each structural char to the nearest
        # MORE-POPULAR column within tolerance that also has an adjacent
        # structural char (row ± 1).
        offsets: list[int] = []
        for col in row_structural:
            offset = self._best_offset(
                row, col, col_counts, structural_positions, grid.height
            )
            offsets.append(offset)

        # ALL structural chars must have the same non-zero offset
        if not offsets or len(set(offsets)) != 1 or offsets[0] == 0:
            return None

        d = offsets[0]

        # Build correction with ALL non-space cells on this row
        row_cells: list[Cell] = []
        for col in range(grid.width):
            cell = grid.get_cell(Position(row=row, col=col))
            if cell is not None and cell.character.value != " ":
                row_cells.append(cell)

        if not row_cells:
            return None

        # Verify correction wouldn't go out of bounds
        for cell in row_cells:
            new_col = cell.position.col - d
            if new_col < 0 or new_col >= grid.width:
                return None

        row_line = Line(cells=row_cells, direction=Direction.HORIZONTAL)
        return ShiftCorrection(
            line=row_line,
            row_offset=0,
            col_offset=-d,
        )

    def _best_offset(
        self,
        row: int,
        col: int,
        col_counts: dict[int, int],
        structural_positions: set[tuple[int, int]],
        grid_height: int,
    ) -> int:
        """
        Find the offset from ``col`` to the best nearby column.

        A nearby column is "better" if:
        - It has strictly more structural chars than ``col``.
        - It meets the minimum consensus threshold.
        - It has a structural char on an adjacent row (``row ± 1``),
          ensuring the correction connects to an existing vertical structure.

        Returns:
            Positive offset if col is right of the best column (shifted right),
            negative if left (shifted left), or 0 if no better column exists.
        """
        my_count = col_counts.get(col, 0)
        best_offset = 0
        best_count = my_count

        for d in range(1, self._tolerance + 1):
            for candidate in [col - d, col + d]:
                candidate_count = col_counts.get(candidate, 0)
                if (
                    candidate_count > best_count
                    and candidate_count >= self._min_consensus
                ):
                    # Adjacency check: the target column must have a
                    # structural char on row-1 or row+1
                    has_adjacent = False
                    if row > 0 and (row - 1, candidate) in structural_positions:
                        has_adjacent = True
                    if (
                        row < grid_height - 1
                        and (row + 1, candidate) in structural_positions
                    ):
                        has_adjacent = True
                    if has_adjacent:
                        best_count = candidate_count
                        best_offset = col - candidate
        return best_offset
