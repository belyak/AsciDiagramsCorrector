"""Parallel line finder for grouping lines that should be aligned."""

from ascii_corrector.detection.protocols import ParallelGroup
from ascii_corrector.domain import Direction, Line


class ParallelLineFinder:
    """
    Finds groups of lines that should be parallel/aligned.

    Groups lines by direction and position proximity, identifying
    lines that may have shifted from their intended positions.
    """

    def __init__(
        self,
        tolerance: int = 1,
        min_overlap_ratio: float = 0.5,
    ) -> None:
        """
        Initialize the parallel line finder.

        Args:
            tolerance: Maximum position difference to consider lines parallel.
            min_overlap_ratio: Minimum overlap ratio for parallel consideration.
        """
        self._tolerance = tolerance
        self._min_overlap_ratio = min_overlap_ratio

    def find_parallel_groups(self, lines: list[Line]) -> list[ParallelGroup]:
        """
        Group lines that should be parallel/aligned.

        Args:
            lines: List of detected lines.

        Returns:
            List of ParallelGroup objects.
        """
        if not lines:
            return []

        # Separate by direction
        horizontal = [ln for ln in lines if ln.direction == Direction.HORIZONTAL]
        vertical = [ln for ln in lines if ln.direction == Direction.VERTICAL]

        groups: list[ParallelGroup] = []

        # Group horizontal lines
        groups.extend(self._group_lines_by_position(horizontal, Direction.HORIZONTAL))

        # Group vertical lines
        groups.extend(self._group_lines_by_position(vertical, Direction.VERTICAL))

        return groups

    def _group_lines_by_position(
        self,
        lines: list[Line],
        direction: Direction,
    ) -> list[ParallelGroup]:
        """
        Group lines by their position with tolerance.

        Args:
            lines: Lines of same direction.
            direction: Direction of lines.

        Returns:
            List of parallel groups.
        """
        if not lines:
            return []

        # Get position function based on direction
        if direction == Direction.HORIZONTAL:
            get_position = lambda ln: ln.dominant_row()
        else:
            get_position = lambda ln: ln.dominant_col()

        # Sort by position
        sorted_lines = sorted(
            [ln for ln in lines if get_position(ln) is not None],
            key=lambda ln: get_position(ln) or 0,
        )

        if not sorted_lines:
            return []

        groups: list[ParallelGroup] = []
        current_group_lines: list[Line] = [sorted_lines[0]]

        for line in sorted_lines[1:]:
            last_pos = get_position(current_group_lines[-1])
            current_pos = get_position(line)

            if last_pos is not None and current_pos is not None:
                if abs(current_pos - last_pos) <= self._tolerance:
                    # Check if lines have sufficient overlap
                    if self._has_sufficient_overlap(current_group_lines[-1], line):
                        current_group_lines.append(line)
                        continue

            # Start new group
            groups.append(self._create_group(current_group_lines, direction))
            current_group_lines = [line]

        # Don't forget the last group
        groups.append(self._create_group(current_group_lines, direction))

        return groups

    def _has_sufficient_overlap(self, line1: Line, line2: Line) -> bool:
        """
        Check if two lines have sufficient overlap to be considered parallel.

        Args:
            line1: First line.
            line2: Second line.

        Returns:
            True if lines overlap sufficiently.
        """
        if line1.direction == Direction.HORIZONTAL:
            # Check column overlap
            start1, end1 = line1.start_position().col, line1.end_position().col
            start2, end2 = line2.start_position().col, line2.end_position().col
        else:
            # Check row overlap
            start1, end1 = line1.start_position().row, line1.end_position().row
            start2, end2 = line2.start_position().row, line2.end_position().row

        # Calculate overlap
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        overlap = max(0, overlap_end - overlap_start + 1)

        # Calculate lengths
        len1 = end1 - start1 + 1
        len2 = end2 - start2 + 1
        min_len = min(len1, len2)

        if min_len == 0:
            return False

        return (overlap / min_len) >= self._min_overlap_ratio

    def _create_group(
        self,
        lines: list[Line],
        direction: Direction,
    ) -> ParallelGroup:
        """
        Create a ParallelGroup from a list of lines.

        Args:
            lines: Lines in the group.
            direction: Direction of lines.

        Returns:
            ParallelGroup with reference line set.
        """
        # Reference is the longest line
        reference = max(lines, key=lambda ln: ln.length())

        # Expected position is the reference line's position
        if direction == Direction.HORIZONTAL:
            expected_position = reference.dominant_row()
        else:
            expected_position = reference.dominant_col()

        return ParallelGroup(
            lines=lines,
            direction=direction,
            reference_line=reference,
            expected_position=expected_position,
        )
