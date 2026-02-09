"""Line detection algorithms for ASCII diagrams."""

from ascii_corrector.domain import Cell, CharacterClass, Direction, Grid, Line, Position
from ascii_corrector.domain.character_constants import (
    BRIDGE_CHARS,
    DIAGONAL_DOWN,
    DIAGONAL_UP,
    HORIZONTAL_CHARS,
    VERTICAL_CHARS,
)


class LineDetector:
    """
    Detects horizontal, vertical, and diagonal lines in ASCII grids.

    Scans the grid for consecutive line characters and groups them
    into Line objects with proper direction and position tracking.
    """

    def __init__(self, min_line_length: int = 2, detect_diagonals: bool = False) -> None:
        """
        Initialize the line detector.

        Args:
            min_line_length: Minimum number of characters to consider a line.
            detect_diagonals: Whether to detect diagonal lines.
        """
        self._min_line_length = min_line_length
        self._detect_diagonals = detect_diagonals

    def detect_lines(self, grid: Grid) -> list[Line]:
        """
        Detect all horizontal, vertical, and optionally diagonal lines in the grid.

        Args:
            grid: Grid to scan for lines.

        Returns:
            List of detected Line objects.
        """
        lines: list[Line] = []

        if grid.width == 0 or grid.height == 0:
            return lines

        # Detect horizontal lines
        lines.extend(self._detect_horizontal_lines(grid))

        # Detect vertical lines
        lines.extend(self._detect_vertical_lines(grid))

        # Detect diagonal lines if enabled
        if self._detect_diagonals:
            lines.extend(self._detect_diagonal_lines(grid))

        return lines

    def _detect_horizontal_lines(self, grid: Grid) -> list[Line]:
        """
        Detect horizontal lines by scanning rows.

        Bridges through ``+`` characters: a ``+`` does not break a line but
        is **not** included in the Line's cells.  This lets horizontal
        segments separated by box corners (``+--+--+``) be detected as a
        single long line.

        Args:
            grid: Grid to scan.

        Returns:
            List of horizontal Line objects.
        """
        lines: list[Line] = []

        for row in range(grid.height):
            col = 0
            while col < grid.width:
                cell = grid.get_cell(Position(row=row, col=col))
                if cell is None:
                    col += 1
                    continue

                char_value = cell.character.value

                # A line can start with a horizontal char directly…
                if char_value in HORIZONTAL_CHARS:
                    line_cells: list[Cell] = [cell]
                    col += 1
                # …or with a bridge char if followed eventually by a horizontal char
                elif char_value in BRIDGE_CHARS:
                    peek = col + 1
                    while peek < grid.width:
                        pc = grid.get_cell(Position(row=row, col=peek))
                        if pc is None:
                            break
                        if pc.character.value in BRIDGE_CHARS:
                            peek += 1
                            continue
                        if pc.character.value in HORIZONTAL_CHARS:
                            break
                        break
                    else:
                        col += 1
                        continue
                    pc = grid.get_cell(Position(row=row, col=peek))
                    if pc is not None and pc.character.value in HORIZONTAL_CHARS:
                        line_cells = []
                        col = col + 1  # skip the starting +
                    else:
                        col += 1
                        continue
                else:
                    col += 1
                    continue

                # Inner scan: collect horizontal chars, bridge through +
                while col < grid.width:
                    next_cell = grid.get_cell(Position(row=row, col=col))
                    if next_cell is None:
                        break
                    nv = next_cell.character.value
                    if nv in HORIZONTAL_CHARS:
                        line_cells.append(next_cell)
                        col += 1
                    elif nv in BRIDGE_CHARS:
                        # Peek past consecutive bridge chars
                        peek = col + 1
                        while peek < grid.width:
                            pc = grid.get_cell(Position(row=row, col=peek))
                            if pc is None:
                                break
                            if pc.character.value in BRIDGE_CHARS:
                                peek += 1
                                continue
                            break
                        pc = grid.get_cell(Position(row=row, col=peek)) if peek < grid.width else None
                        if pc is not None and pc.character.value in HORIZONTAL_CHARS:
                            col = peek  # skip bridge chars, continue scanning
                        else:
                            break
                    else:
                        break

                if len(line_cells) >= self._min_line_length:
                    lines.append(
                        Line(cells=line_cells, direction=Direction.HORIZONTAL)
                    )

        return lines

    def _detect_vertical_lines(self, grid: Grid) -> list[Line]:
        """
        Detect vertical lines by scanning columns.

        Bridges through ``+`` characters: a ``+`` does not break a line but
        is **not** included in the Line's cells.  This lets vertical segments
        separated by box corners be detected as a single long line.

        Args:
            grid: Grid to scan.

        Returns:
            List of vertical Line objects.
        """
        lines: list[Line] = []

        for col in range(grid.width):
            row = 0
            while row < grid.height:
                cell = grid.get_cell(Position(row=row, col=col))
                if cell is None:
                    row += 1
                    continue

                char_value = cell.character.value

                if char_value in VERTICAL_CHARS:
                    line_cells: list[Cell] = [cell]
                    row += 1
                elif char_value in BRIDGE_CHARS:
                    peek = row + 1
                    while peek < grid.height:
                        pc = grid.get_cell(Position(row=peek, col=col))
                        if pc is None:
                            break
                        if pc.character.value in BRIDGE_CHARS:
                            peek += 1
                            continue
                        if pc.character.value in VERTICAL_CHARS:
                            break
                        break
                    else:
                        row += 1
                        continue
                    pc = grid.get_cell(Position(row=peek, col=col))
                    if pc is not None and pc.character.value in VERTICAL_CHARS:
                        line_cells = []
                        row = row + 1  # skip the starting +
                    else:
                        row += 1
                        continue
                else:
                    row += 1
                    continue

                # Inner scan: collect vertical chars, bridge through +
                while row < grid.height:
                    next_cell = grid.get_cell(Position(row=row, col=col))
                    if next_cell is None:
                        break
                    nv = next_cell.character.value
                    if nv in VERTICAL_CHARS:
                        line_cells.append(next_cell)
                        row += 1
                    elif nv in BRIDGE_CHARS:
                        peek = row + 1
                        while peek < grid.height:
                            pc = grid.get_cell(Position(row=peek, col=col))
                            if pc is None:
                                break
                            if pc.character.value in BRIDGE_CHARS:
                                peek += 1
                                continue
                            break
                        pc = grid.get_cell(Position(row=peek, col=col)) if peek < grid.height else None
                        if pc is not None and pc.character.value in VERTICAL_CHARS:
                            row = peek  # skip bridge chars, continue scanning
                        else:
                            break
                    else:
                        break

                if len(line_cells) >= self._min_line_length:
                    lines.append(
                        Line(cells=line_cells, direction=Direction.VERTICAL)
                    )

        return lines

    def _detect_diagonal_lines(self, grid: Grid) -> list[Line]:
        r"""
        Detect diagonal lines by scanning diagonally through the grid.

        Detects both down-right (\) and up-right (/) diagonals.

        Args:
            grid: Grid to scan.

        Returns:
            List of diagonal Line objects.
        """
        lines: list[Line] = []

        # Detect down-right diagonals (\)
        lines.extend(self._detect_diagonal_down_right(grid))

        # Detect up-right diagonals (/)
        lines.extend(self._detect_diagonal_up_right(grid))

        return lines

    def _detect_diagonal_down_right(self, grid: Grid) -> list[Line]:
        r"""
        Detect diagonal lines going down-right (\).

        Args:
            grid: Grid to scan.

        Returns:
            List of down-right diagonal Line objects.
        """
        lines: list[Line] = []
        visited: set[tuple[int, int]] = set()

        # Start from each position and try to build diagonal
        for start_row in range(grid.height):
            for start_col in range(grid.width):
                if (start_row, start_col) in visited:
                    continue

                cell = grid.get_cell(Position(row=start_row, col=start_col))
                if cell is None or cell.character.value not in DIAGONAL_DOWN:
                    continue

                # Try to extend diagonally down-right
                line_cells: list[Cell] = [cell]
                row, col = start_row + 1, start_col + 1

                while row < grid.height and col < grid.width:
                    if (row, col) in visited:
                        break
                    next_cell = grid.get_cell(Position(row=row, col=col))
                    if next_cell is None or next_cell.character.value not in DIAGONAL_DOWN:
                        break
                    line_cells.append(next_cell)
                    row += 1
                    col += 1

                # Only mark as visited if we created a line
                if len(line_cells) >= self._min_line_length:
                    lines.append(
                        Line(cells=line_cells, direction=Direction.DIAGONAL_DOWN)
                    )
                    # Mark all cells in this line as visited
                    for cell in line_cells:
                        visited.add((cell.position.row, cell.position.col))

        return lines

    def _detect_diagonal_up_right(self, grid: Grid) -> list[Line]:
        r"""
        Detect diagonal lines going up-right (/).

        Args:
            grid: Grid to scan.

        Returns:
            List of up-right diagonal Line objects.
        """
        lines: list[Line] = []
        visited: set[tuple[int, int]] = set()

        # Start from each position and try to build diagonal
        for start_row in range(grid.height):
            for start_col in range(grid.width):
                if (start_row, start_col) in visited:
                    continue

                cell = grid.get_cell(Position(row=start_row, col=start_col))
                if cell is None or cell.character.value not in DIAGONAL_UP:
                    continue

                # Try to extend diagonally up-right
                line_cells: list[Cell] = [cell]
                row, col = start_row - 1, start_col + 1

                while row >= 0 and col < grid.width:
                    if (row, col) in visited:
                        break
                    next_cell = grid.get_cell(Position(row=row, col=col))
                    if next_cell is None or next_cell.character.value not in DIAGONAL_UP:
                        break
                    line_cells.append(next_cell)
                    row -= 1
                    col += 1

                # Only mark as visited if we created a line
                if len(line_cells) >= self._min_line_length:
                    lines.append(
                        Line(cells=line_cells, direction=Direction.DIAGONAL_UP)
                    )
                    # Mark all cells in this line as visited
                    for cell in line_cells:
                        visited.add((cell.position.row, cell.position.col))

        return lines
