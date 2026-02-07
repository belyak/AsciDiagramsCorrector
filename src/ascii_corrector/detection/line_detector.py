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
    # Characters that bridge line segments without being included in the line
    BRIDGE_CHARS: frozenset[str] = frozenset({"+"})

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
                if char_value in self.HORIZONTAL_CHARS:
                    line_cells: list[Cell] = [cell]
                    col += 1
                # …or with a bridge char if followed eventually by a horizontal char
                elif char_value in self.BRIDGE_CHARS:
                    peek = col + 1
                    while peek < grid.width:
                        pc = grid.get_cell(Position(row=row, col=peek))
                        if pc is None:
                            break
                        if pc.character.value in self.BRIDGE_CHARS:
                            peek += 1
                            continue
                        if pc.character.value in self.HORIZONTAL_CHARS:
                            break
                        break
                    else:
                        col += 1
                        continue
                    pc = grid.get_cell(Position(row=row, col=peek))
                    if pc is not None and pc.character.value in self.HORIZONTAL_CHARS:
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
                    if nv in self.HORIZONTAL_CHARS:
                        line_cells.append(next_cell)
                        col += 1
                    elif nv in self.BRIDGE_CHARS:
                        # Peek past consecutive bridge chars
                        peek = col + 1
                        while peek < grid.width:
                            pc = grid.get_cell(Position(row=row, col=peek))
                            if pc is None:
                                break
                            if pc.character.value in self.BRIDGE_CHARS:
                                peek += 1
                                continue
                            break
                        pc = grid.get_cell(Position(row=row, col=peek)) if peek < grid.width else None
                        if pc is not None and pc.character.value in self.HORIZONTAL_CHARS:
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

                if char_value in self.VERTICAL_CHARS:
                    line_cells: list[Cell] = [cell]
                    row += 1
                elif char_value in self.BRIDGE_CHARS:
                    peek = row + 1
                    while peek < grid.height:
                        pc = grid.get_cell(Position(row=peek, col=col))
                        if pc is None:
                            break
                        if pc.character.value in self.BRIDGE_CHARS:
                            peek += 1
                            continue
                        if pc.character.value in self.VERTICAL_CHARS:
                            break
                        break
                    else:
                        row += 1
                        continue
                    pc = grid.get_cell(Position(row=peek, col=col))
                    if pc is not None and pc.character.value in self.VERTICAL_CHARS:
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
                    if nv in self.VERTICAL_CHARS:
                        line_cells.append(next_cell)
                        row += 1
                    elif nv in self.BRIDGE_CHARS:
                        peek = row + 1
                        while peek < grid.height:
                            pc = grid.get_cell(Position(row=peek, col=col))
                            if pc is None:
                                break
                            if pc.character.value in self.BRIDGE_CHARS:
                                peek += 1
                                continue
                            break
                        pc = grid.get_cell(Position(row=peek, col=col)) if peek < grid.height else None
                        if pc is not None and pc.character.value in self.VERTICAL_CHARS:
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
