"""Stray character finder for detecting misaligned individual line characters."""

from ascii_corrector.correction.protocols import ShiftCorrection
from ascii_corrector.domain import Cell, Direction, Grid, Line, Position
from ascii_corrector.domain.character_constants import CORNER_CHARS, HORIZONTAL_CHARS, VERTICAL_CHARS


class StrayCharacterFinder:
    """
    Finds individual line characters not part of any detected line and
    produces corrections to align them with the nearest detected line.
    """

    def __init__(self, tolerance: int = 1) -> None:
        self._tolerance = tolerance

    def find_stray_corrections(
        self, grid: Grid, detected_lines: list[Line]
    ) -> list[ShiftCorrection]:
        """
        Find corrections for stray characters near detected lines.

        Scans the grid for ``|``/``!`` and ``-``/``=``/``_`` characters that
        are NOT part of any detected line.  For each stray, finds the nearest
        detected line of matching direction within *tolerance* and produces
        a ``ShiftCorrection`` to move the stray to the correct position.

        A stray is only corrected when the space between it and the next
        pipe/edge in both horizontal directions contains **only whitespace**.
        This prevents moving box edges that have text content between them,
        which would break formatting.

        Args:
            grid: The grid to scan.
            detected_lines: Lines already detected by LineDetector.

        Returns:
            List of ShiftCorrection objects for stray characters.
        """
        # Build set of positions already covered by detected lines
        covered: set[Position] = set()
        for line in detected_lines:
            for cell in line.cells:
                covered.add(cell.position)

        vertical_lines = [ln for ln in detected_lines if ln.direction == Direction.VERTICAL]
        horizontal_lines = [ln for ln in detected_lines if ln.direction == Direction.HORIZONTAL]

        corrections: list[ShiftCorrection] = []

        for row in range(grid.height):
            for col in range(grid.width):
                pos = Position(row=row, col=col)
                if pos in covered:
                    continue

                cell = grid.get_cell(pos)
                if cell is None:
                    continue

                char_value = cell.character.value

                if char_value in VERTICAL_CHARS:
                    corr = self._find_vertical_correction(
                        cell, vertical_lines, grid
                    )
                    if corr is not None:
                        corrections.append(corr)
                elif char_value in HORIZONTAL_CHARS:
                    corr = self._find_horizontal_correction(
                        cell, horizontal_lines, grid
                    )
                    if corr is not None:
                        corrections.append(corr)

        return corrections

    @staticmethod
    def _row_has_text(grid: Grid, row: int) -> bool:
        """Return True if the row contains characters other than whitespace
        and vertical-line characters (``|``, ``!``).

        Rows with text content should not have their pipe characters moved
        independently because the text was placed relative to the pipe
        positions, and moving only the pipes would break formatting.
        """
        for c in range(grid.width):
            cell = grid.get_cell(Position(row=row, col=c))
            if cell is None:
                continue
            v = cell.character.value
            if v != " " and v not in VERTICAL_CHARS:
                return True
        return False

    @staticmethod
    def _col_has_text(grid: Grid, col: int) -> bool:
        """Return True if the column contains characters other than whitespace
        and horizontal-line characters (``-``, ``=``, ``_``).
        """
        for r in range(grid.height):
            cell = grid.get_cell(Position(row=r, col=col))
            if cell is None:
                continue
            v = cell.character.value
            if v != " " and v not in HORIZONTAL_CHARS:
                return True
        return False

    @staticmethod
    def _has_adjacent_structural(grid: Grid, row: int, col: int) -> bool:
        """Return True if a structural char (vertical or corner) exists
        at (row-1, col) or (row+1, col).
        """
        structural = VERTICAL_CHARS | CORNER_CHARS
        for adj_row in [row - 1, row + 1]:
            cell = grid.get_cell(Position(row=adj_row, col=col))
            if cell is not None and cell.character.value in structural:
                return True
        return False

    @staticmethod
    def _is_right_edge(grid: Grid, row: int, col: int) -> bool:
        """Return True if (row, col) is the rightmost non-space character.

        A right-edge pipe sits at the boundary of the row's visible content
        with only whitespace between it and the grid edge.  Moving it adjusts
        right padding rather than breaking text layout, so it is safe to
        correct even on rows that contain text.
        """
        return all(
            grid.get_cell(Position(row=row, col=c)) is None
            or grid.get_cell(Position(row=row, col=c)).character.value == " "
            for c in range(col + 1, grid.width)
        )

    def _find_vertical_correction(
        self, stray: Cell, vertical_lines: list[Line], grid: Grid
    ) -> ShiftCorrection | None:
        """Find a correction for a stray vertical character."""
        is_edge = self._is_right_edge(grid, stray.position.row, stray.position.col)

        # Skip if the row has text content — moving just the pipe without
        # the text would break formatting.  Exception: right-edge chars
        # only affect padding, so allow them.
        if self._row_has_text(grid, stray.position.row) and not is_edge:
            return None

        best_line: Line | None = None
        best_distance: int | None = None

        for line in vertical_lines:
            line_col = line.dominant_col()
            if line_col is None:
                continue

            distance = abs(stray.position.col - line_col)
            if distance == 0 or distance > self._tolerance:
                continue

            # Check stray row is within line's row range (± tolerance).
            start_row = line.start_position().row
            end_row = line.end_position().row
            in_range = (
                stray.position.row >= start_row - self._tolerance
                and stray.position.row <= end_row + self._tolerance
            )
            if not in_range:
                # For right-edge chars, use adjacency check instead:
                # require a structural char at the target column on
                # an adjacent row (row ± 1).
                if is_edge and self._has_adjacent_structural(
                    grid, stray.position.row, line_col
                ):
                    pass  # allow — connected to structure
                else:
                    continue

            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_line = line

        if best_line is None or best_distance is None:
            return None

        target_col = best_line.dominant_col()
        if target_col is None:
            return None

        # Verify target position is a space
        target_pos = Position(row=stray.position.row, col=target_col)
        target_cell = grid.get_cell(target_pos)
        if target_cell is None or target_cell.character.value != " ":
            return None

        col_offset = target_col - stray.position.col
        stray_line = Line(cells=[stray], direction=Direction.VERTICAL)
        return ShiftCorrection(
            line=stray_line,
            row_offset=0,
            col_offset=col_offset,
        )

    def _find_horizontal_correction(
        self, stray: Cell, horizontal_lines: list[Line], grid: Grid
    ) -> ShiftCorrection | None:
        """Find a correction for a stray horizontal character."""
        # Skip if the column has text content — moving just the dash without
        # surrounding content would break formatting.
        if self._col_has_text(grid, stray.position.col):
            return None

        best_line: Line | None = None
        best_distance: int | None = None

        for line in horizontal_lines:
            line_row = line.dominant_row()
            if line_row is None:
                continue

            distance = abs(stray.position.row - line_row)
            if distance == 0 or distance > self._tolerance:
                continue

            # Check stray col is within line's col range (± tolerance)
            start_col = line.start_position().col
            end_col = line.end_position().col
            if (
                stray.position.col < start_col - self._tolerance
                or stray.position.col > end_col + self._tolerance
            ):
                continue

            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_line = line

        if best_line is None or best_distance is None:
            return None

        target_row = best_line.dominant_row()
        if target_row is None:
            return None

        # Verify target position is a space
        target_pos = Position(row=target_row, col=stray.position.col)
        target_cell = grid.get_cell(target_pos)
        if target_cell is None or target_cell.character.value != " ":
            return None

        row_offset = target_row - stray.position.row
        stray_line = Line(cells=[stray], direction=Direction.HORIZONTAL)
        return ShiftCorrection(
            line=stray_line,
            row_offset=row_offset,
            col_offset=0,
        )
