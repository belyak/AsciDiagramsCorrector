"""Box structure detection for ASCII diagrams."""

from dataclasses import dataclass

from ascii_corrector.domain import Grid, Line, Position
from ascii_corrector.domain.character_constants import CORNER_CHARS, HORIZONTAL_CHARS, VERTICAL_CHARS


@dataclass(frozen=True)
class BoxStructure:
    """Rectangular box with four edges."""

    top_line: Line
    bottom_line: Line
    left_line: Line
    right_line: Line
    height: int
    width: int


class BoxDetector:
    """Detects rectangular box structures by tracing from corners."""

    def __init__(self, min_size: int = 2) -> None:
        """Initialize the box detector.

        Args:
            min_size: Minimum box dimension (width and height) to consider valid.
        """
        self._min_size = min_size

    def detect_boxes(self, grid: Grid) -> list[BoxStructure]:
        """Find all rectangular boxes by tracing from corners.

        Args:
            grid: Grid to scan for boxes.

        Returns:
            List of detected BoxStructure objects.
        """
        if grid.width == 0 or grid.height == 0:
            return []

        # Find all potential corner characters
        corners = self._find_corners(grid)

        # Try to form boxes from each corner
        boxes = []
        used_boxes = set()  # Track box positions to avoid duplicates

        for top_left in corners:
            box = self._try_form_box(grid, top_left)
            if box:
                # Use a canonical representation to avoid duplicates
                box_id = (
                    box.top_line.dominant_row(),
                    box.left_line.dominant_col(),
                    box.height,
                    box.width,
                )
                if box_id not in used_boxes:
                    boxes.append(box)
                    used_boxes.add(box_id)

        return boxes

    def _find_corners(self, grid: Grid) -> list[Position]:
        """Find all corner characters that could be box corners.

        Args:
            grid: Grid to scan.

        Returns:
            List of corner positions.
        """
        corners = []
        for row in range(grid.height):
            for col in range(grid.width):
                cell = grid.get_cell(Position(row=row, col=col))
                if cell and cell.character.value in CORNER_CHARS:
                    corners.append(Position(row=row, col=col))
        return corners

    def _try_form_box(self, grid: Grid, top_left: Position) -> BoxStructure | None:
        """Try to form a box from a top-left corner.

        Traces horizontally to find top-right corner, then down and left to
        find bottom corners.

        Args:
            grid: Grid to scan.
            top_left: Position of potential top-left corner.

        Returns:
            BoxStructure if a valid box is found, None otherwise.
        """
        # Find top-right corner by tracing right
        top_right = self._trace_horizontal(grid, top_left)
        if top_right is None:
            return None

        width = top_right.col - top_left.col + 1
        if width < self._min_size:
            return None

        # Find bottom-left corner by tracing down
        bottom_left = self._trace_vertical(grid, top_left)
        if bottom_left is None:
            return None

        height = bottom_left.row - top_left.row + 1
        if height < self._min_size:
            return None

        # Verify bottom-right corner exists
        bottom_right = Position(row=bottom_left.row, col=top_right.col)
        cell_br = grid.get_cell(bottom_right)
        if cell_br is None or cell_br.character.value not in CORNER_CHARS:
            return None

        # Build Line objects for each edge
        top_line = self._build_horizontal_line(grid, top_left, top_right)
        bottom_line = self._build_horizontal_line(grid, bottom_left, bottom_right)
        left_line = self._build_vertical_line(grid, top_left, bottom_left)
        right_line = self._build_vertical_line(grid, top_right, bottom_right)

        if not (top_line and bottom_line and left_line and right_line):
            return None

        return BoxStructure(
            top_line=top_line,
            bottom_line=bottom_line,
            left_line=left_line,
            right_line=right_line,
            height=height,
            width=width,
        )

    def _trace_horizontal(self, grid: Grid, start: Position) -> Position | None:
        """Trace horizontally right from start position to find corner.

        Args:
            grid: Grid to scan.
            start: Starting position (should be a corner).

        Returns:
            Position of next corner, or None if not found.
        """
        col = start.col + 1
        while col < grid.width:
            cell = grid.get_cell(Position(row=start.row, col=col))
            if cell is None:
                break
            if cell.character.value in HORIZONTAL_CHARS:
                col += 1
                continue
            if cell.character.value in CORNER_CHARS:
                return Position(row=start.row, col=col)
            break
        return None

    def _trace_vertical(self, grid: Grid, start: Position) -> Position | None:
        """Trace vertically down from start position to find corner.

        Args:
            grid: Grid to scan.
            start: Starting position (should be a corner).

        Returns:
            Position of next corner, or None if not found.
        """
        row = start.row + 1
        while row < grid.height:
            cell = grid.get_cell(Position(row=row, col=start.col))
            if cell is None:
                break
            if cell.character.value in VERTICAL_CHARS:
                row += 1
                continue
            if cell.character.value in CORNER_CHARS:
                return Position(row=row, col=start.col)
            break
        return None

    def _build_horizontal_line(
        self, grid: Grid, left: Position, right: Position
    ) -> Line | None:
        """Build a horizontal Line from left corner to right corner.

        Args:
            grid: Grid to scan.
            left: Left corner position.
            right: Right corner position.

        Returns:
            Line object, or None if insufficient characters found.
        """
        from ascii_corrector.domain import Cell, Direction

        cells: list[Cell] = []
        for col in range(left.col, right.col + 1):
            cell = grid.get_cell(Position(row=left.row, col=col))
            if cell and cell.character.value in (HORIZONTAL_CHARS | CORNER_CHARS):
                cells.append(cell)

        if len(cells) < 2:
            return None

        return Line(cells=cells, direction=Direction.HORIZONTAL)

    def _build_vertical_line(
        self, grid: Grid, top: Position, bottom: Position
    ) -> Line | None:
        """Build a vertical Line from top corner to bottom corner.

        Args:
            grid: Grid to scan.
            top: Top corner position.
            bottom: Bottom corner position.

        Returns:
            Line object, or None if insufficient characters found.
        """
        from ascii_corrector.domain import Cell, Direction

        cells: list[Cell] = []
        for row in range(top.row, bottom.row + 1):
            cell = grid.get_cell(Position(row=row, col=top.col))
            if cell and cell.character.value in (VERTICAL_CHARS | CORNER_CHARS):
                cells.append(cell)

        if len(cells) < 2:
            return None

        return Line(cells=cells, direction=Direction.VERTICAL)
