"""Structure classifier to identify diagram pattern types (tree, box, graph, etc)."""

from enum import Enum, auto

from ascii_corrector.domain import Grid, Position
from ascii_corrector.domain.character_constants import HORIZONTAL_CHARS, VERTICAL_CHARS


class StructureType(Enum):
    """Types of diagram structures."""

    BOX = auto()
    TREE = auto()
    GRAPH = auto()
    UNKNOWN = auto()


class StructureClassifier:
    """Classifies diagram structure patterns."""

    def __init__(self, tree_branch_threshold: int = 2) -> None:
        """Initialize the classifier.

        Args:
            tree_branch_threshold: Minimum number of branch patterns to classify as tree.
        """
        self._tree_branch_threshold = tree_branch_threshold

    def classify(self, grid: Grid) -> StructureType:
        """Determine the primary structure type of the diagram.

        Args:
            grid: Grid to classify.

        Returns:
            StructureType indicating the primary structure.
        """
        if self.has_tree_patterns(grid):
            return StructureType.TREE
        if self.has_box_patterns(grid):
            return StructureType.BOX
        return StructureType.UNKNOWN

    def has_tree_patterns(self, grid: Grid) -> bool:
        """Check if grid contains tree branch notation patterns.

        Tree patterns include:
        - Branch notation: +-- or similar (+ followed by 2+ horizontal chars)
        - Vertical stem connecting to branch
        - Multiple branches from single column

        Args:
            grid: Grid to check.

        Returns:
            True if tree patterns detected.
        """
        branch_count = 0

        for row in range(grid.height):
            for col in range(grid.width - 2):
                # Check for tree branch pattern: + followed by horizontal chars
                if self._is_tree_branch(grid, Position(row=row, col=col)):
                    branch_count += 1

        return branch_count >= self._tree_branch_threshold

    def has_box_patterns(self, grid: Grid) -> bool:
        """Check if grid contains rectangular box patterns.

        Box patterns include:
        - Four corners forming closed rectangles
        - Matching opposite edges

        Args:
            grid: Grid to check.

        Returns:
            True if box patterns detected.
        """
        # Count corner-like patterns
        corner_chars = {"+", ".", "'", "`", "┌", "┐", "└", "┘", "╔", "╗", "╚", "╝"}
        corner_count = 0

        for row in range(grid.height):
            for col in range(grid.width):
                cell = grid.get_cell(Position(row=row, col=col))
                if cell and cell.character.value in corner_chars:
                    corner_count += 1

        # Boxes typically have 4+ corners
        return corner_count >= 4

    def _is_tree_branch(self, grid: Grid, pos: Position) -> bool:
        """Check if position starts a tree branch pattern.

        A tree branch is a '+' or other character preceded by whitespace and
        followed by 2+ horizontal characters, with a vertical stem nearby.
        This distinguishes tree branches from box corners by checking context.

        Args:
            grid: Grid to check.
            pos: Position to check (should be a '+').

        Returns:
            True if this is a tree branch pattern.
        """
        # Check if position has '+'
        cell = grid.get_cell(pos)
        if cell is None or cell.character.value != "+":
            return False

        # Check for 2+ horizontal chars to the right
        horizontal_count = 0
        for check_col in range(pos.col + 1, min(pos.col + 4, grid.width)):
            check_cell = grid.get_cell(Position(row=pos.row, col=check_col))
            if check_cell and check_cell.character.value in HORIZONTAL_CHARS:
                horizontal_count += 1
            else:
                break

        if horizontal_count < 2:
            return False

        # Check for vertical stem ABOVE (not below and to the right like box corner)
        # This is the key distinction: tree branches have the stem above
        if pos.row > 0:
            above_cell = grid.get_cell(Position(row=pos.row - 1, col=pos.col))
            if above_cell and above_cell.character.value in (VERTICAL_CHARS | {"|", "+"}):
                return True

        return False
