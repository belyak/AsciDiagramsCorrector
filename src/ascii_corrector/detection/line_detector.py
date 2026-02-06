"""Line detection algorithms for ASCII diagrams."""

from ascii_corrector.domain import Cell, CharacterClass, Direction, Grid, Line, Position


class LineDetector:
    """
    Detects horizontal and vertical lines in ASCII grids.

    Scans the grid for consecutive line characters and groups them
    into Line objects with proper direction and position tracking.
    """

    # Characters that form horizontal lines
    HORIZONTAL_CHARS: frozenset[str] = frozenset({"-", "=", "_"})
    # Characters that form vertical lines
    VERTICAL_CHARS: frozenset[str] = frozenset({"|", "!"})

    def __init__(self, min_line_length: int = 2) -> None:
        """
        Initialize the line detector.

        Args:
            min_line_length: Minimum number of characters to consider a line.
        """
        self._min_line_length = min_line_length

    def detect_lines(self, grid: Grid) -> list[Line]:
        """
        Detect all horizontal and vertical lines in the grid.

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

        return lines

    def _detect_horizontal_lines(self, grid: Grid) -> list[Line]:
        """
        Detect horizontal lines by scanning rows.

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
                if char_value in self.HORIZONTAL_CHARS:
                    # Found start of potential line
                    line_cells: list[Cell] = [cell]
                    start_col = col
                    col += 1

                    # Continue while same character type
                    while col < grid.width:
                        next_cell = grid.get_cell(Position(row=row, col=col))
                        if next_cell is None:
                            break
                        if next_cell.character.value in self.HORIZONTAL_CHARS:
                            line_cells.append(next_cell)
                            col += 1
                        else:
                            break

                    # Check if line meets minimum length
                    if len(line_cells) >= self._min_line_length:
                        lines.append(
                            Line(cells=line_cells, direction=Direction.HORIZONTAL)
                        )
                else:
                    col += 1

        return lines

    def _detect_vertical_lines(self, grid: Grid) -> list[Line]:
        """
        Detect vertical lines by scanning columns.

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
                if char_value in self.VERTICAL_CHARS:
                    # Found start of potential line
                    line_cells: list[Cell] = [cell]
                    row += 1

                    # Continue while same character type
                    while row < grid.height:
                        next_cell = grid.get_cell(Position(row=row, col=col))
                        if next_cell is None:
                            break
                        if next_cell.character.value in self.VERTICAL_CHARS:
                            line_cells.append(next_cell)
                            row += 1
                        else:
                            break

                    # Check if line meets minimum length
                    if len(line_cells) >= self._min_line_length:
                        lines.append(
                            Line(cells=line_cells, direction=Direction.VERTICAL)
                        )
                else:
                    row += 1

        return lines
