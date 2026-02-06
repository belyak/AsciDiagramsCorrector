"""Shift corrector for applying alignment corrections to grids."""

from ascii_corrector.correction.protocols import ShiftCorrection
from ascii_corrector.domain import Character, Grid, Position


class ShiftCorrector:
    """
    Applies shift corrections to ASCII diagram grids.

    Takes a ShiftCorrection and applies the specified offset to the
    line's cells in the grid, clearing original positions and placing
    characters at new positions.
    """

    def apply_correction(
        self,
        correction: ShiftCorrection,
        grid: Grid,
    ) -> Grid:
        """
        Apply a shift correction to the grid.

        Args:
            correction: The correction to apply.
            grid: The grid to modify.

        Returns:
            New grid with correction applied.

        Raises:
            ValueError: If correction would move cells out of bounds.
        """
        # Always work on a copy
        result = grid.copy()

        # If no offset, just return the copy
        if correction.row_offset == 0 and correction.col_offset == 0:
            return result

        # Validate all new positions are in bounds
        for cell in correction.line.cells:
            new_pos = Position(
                row=cell.position.row + correction.row_offset,
                col=cell.position.col + correction.col_offset,
            )
            if not result.is_valid_position(new_pos):
                raise ValueError(
                    f"Correction would move cell to out of bounds position: {new_pos}"
                )

        # Clear original positions first
        for cell in correction.line.cells:
            result.clear_cell(cell.position)

        # Place characters at new positions
        for cell in correction.line.cells:
            new_pos = Position(
                row=cell.position.row + correction.row_offset,
                col=cell.position.col + correction.col_offset,
            )
            result.set_cell(new_pos, cell.character)

        return result

    def apply_corrections(
        self,
        corrections: list[ShiftCorrection],
        grid: Grid,
    ) -> Grid:
        """
        Apply multiple corrections to a grid.

        Args:
            corrections: List of corrections to apply.
            grid: The grid to modify.

        Returns:
            New grid with all corrections applied.
        """
        result = grid.copy()

        for correction in corrections:
            result = self.apply_correction(correction, result)

        return result
