"""Alignment calculator for box structures."""

from ascii_corrector.correction.protocols import ShiftCorrection
from ascii_corrector.detection.box_detector import BoxStructure
from ascii_corrector.domain import Direction


class BoxAlignmentCalculator:
    """Calculates corrections to align box edges vertically and horizontally."""

    def __init__(self, tolerance: int = 1) -> None:
        """Initialize the calculator.

        Args:
            tolerance: Row/column offset tolerance for alignment (not used in basic version).
        """
        self._tolerance = tolerance

    def calculate_corrections(self, boxes: list[BoxStructure]) -> list[ShiftCorrection]:
        """Generate corrections to align each box's edges.

        For each box, ensures:
        - Left and right edges are vertically aligned
        - Top and bottom edges are horizontally aligned
        - Width and height are consistent

        Args:
            boxes: List of detected boxes.

        Returns:
            List of ShiftCorrection objects to align box edges.
        """
        corrections: list[ShiftCorrection] = []

        for box in boxes:
            corrections.extend(self._align_box_edges(box))

        return corrections

    def _align_box_edges(self, box: BoxStructure) -> list[ShiftCorrection]:
        """Calculate corrections for a single box.

        Aligns left and right vertical edges to the left edge position,
        aligns top and bottom horizontal edges to the top edge position.

        Args:
            box: Box structure to align.

        Returns:
            List of ShiftCorrection objects for this box.
        """
        corrections: list[ShiftCorrection] = []

        # Get reference positions (left edge position and top edge position)
        ref_col = box.left_line.dominant_col()
        ref_row = box.top_line.dominant_row()

        if ref_col is None or ref_row is None:
            return corrections

        # Align right edge to reference column (left edge column + width - 1)
        target_right_col = ref_col + box.width - 1
        right_col = box.right_line.dominant_col()
        if right_col is not None and right_col != target_right_col:
            col_offset = target_right_col - right_col
            corrections.append(
                ShiftCorrection(
                    line=box.right_line,
                    row_offset=0,
                    col_offset=col_offset,
                )
            )

        # Align bottom edge to reference row (top edge row + height - 1)
        target_bottom_row = ref_row + box.height - 1
        bottom_row = box.bottom_line.dominant_row()
        if bottom_row is not None and bottom_row != target_bottom_row:
            row_offset = target_bottom_row - bottom_row
            corrections.append(
                ShiftCorrection(
                    line=box.bottom_line,
                    row_offset=row_offset,
                    col_offset=0,
                )
            )

        return corrections
