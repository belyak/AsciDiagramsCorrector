"""Alignment calculator for parallel line groups."""

from ascii_corrector.correction.protocols import AlignmentResult, ShiftCorrection
from ascii_corrector.detection.protocols import ParallelGroup
from ascii_corrector.domain import Direction, Line


class AlignmentCalculator:
    """
    Calculates alignment corrections for parallel line groups.

    Determines the offset needed for each misaligned line to align
    with the reference line in a parallel group.
    """

    def calculate_alignment(self, group: ParallelGroup) -> AlignmentResult:
        """
        Calculate alignment corrections for a parallel group.

        Args:
            group: ParallelGroup containing lines to align.

        Returns:
            AlignmentResult with corrections for misaligned lines.
        """
        if not group.lines:
            return AlignmentResult(group=group, corrections=[])

        reference = group.reference_line
        if reference is None:
            # Use first line as reference if not set
            reference = group.lines[0]

        expected_position = group.expected_position
        if expected_position is None:
            if group.direction == Direction.HORIZONTAL:
                expected_position = reference.dominant_row()
            else:
                expected_position = reference.dominant_col()

        corrections: list[ShiftCorrection] = []

        for line in group.lines:
            if line == reference:
                continue

            correction = self._calculate_line_correction(
                line=line,
                expected_position=expected_position,
                direction=group.direction,
            )

            if correction is not None:
                corrections.append(correction)

        return AlignmentResult(
            group=group,
            corrections=corrections,
            reference_position=expected_position,
        )

    def _calculate_line_correction(
        self,
        line: Line,
        expected_position: int | None,
        direction: Direction,
    ) -> ShiftCorrection | None:
        """
        Calculate correction for a single line.

        Args:
            line: Line to calculate correction for.
            expected_position: Target position (row or column).
            direction: Direction of the line.

        Returns:
            ShiftCorrection if line needs correction, None otherwise.
        """
        if expected_position is None:
            return None

        if direction == Direction.HORIZONTAL:
            current_position = line.dominant_row()
            if current_position is None:
                return None

            offset = expected_position - current_position
            if offset == 0:
                return None

            return ShiftCorrection(
                line=line,
                row_offset=offset,
                col_offset=0,
                confidence=1.0,
            )
        else:
            current_position = line.dominant_col()
            if current_position is None:
                return None

            offset = expected_position - current_position
            if offset == 0:
                return None

            return ShiftCorrection(
                line=line,
                row_offset=0,
                col_offset=offset,
                confidence=1.0,
            )
