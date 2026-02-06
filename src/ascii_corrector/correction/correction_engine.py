"""Correction engine orchestrating the full correction pipeline."""

from ascii_corrector.correction.alignment_calculator import AlignmentCalculator
from ascii_corrector.correction.protocols import CorrectionResult, ShiftCorrection
from ascii_corrector.correction.shift_corrector import ShiftCorrector
from ascii_corrector.detection import LineDetector, ParallelGroup, ParallelLineFinder
from ascii_corrector.domain import Grid


class CorrectionEngine:
    """
    Main orchestrator for the ASCII diagram correction pipeline.

    Coordinates detection, alignment calculation, and correction application
    to fix shifted parallel lines in ASCII diagrams.
    """

    def __init__(
        self,
        tolerance: int = 1,
        min_line_length: int = 2,
        min_overlap_ratio: float = 0.5,
    ) -> None:
        """
        Initialize the correction engine.

        Args:
            tolerance: Position tolerance for parallel line grouping.
            min_line_length: Minimum characters to consider a line.
            min_overlap_ratio: Minimum overlap ratio for parallel detection.
        """
        self._tolerance = tolerance
        self._min_line_length = min_line_length
        self._min_overlap_ratio = min_overlap_ratio

        # Initialize components
        self._line_detector = LineDetector(min_line_length=min_line_length)
        self._parallel_finder = ParallelLineFinder(
            tolerance=tolerance,
            min_overlap_ratio=min_overlap_ratio,
        )
        self._alignment_calculator = AlignmentCalculator()
        self._shift_corrector = ShiftCorrector()

    def correct(self, grid: Grid) -> CorrectionResult:
        """
        Apply all corrections to a grid.

        Pipeline:
        1. Detect lines in the grid
        2. Find parallel line groups
        3. Calculate alignment corrections for each group
        4. Apply corrections to the grid

        Args:
            grid: Grid to correct.

        Returns:
            CorrectionResult with original and corrected grids.
        """
        # Detect lines
        lines = self._line_detector.detect_lines(grid)

        if not lines:
            return CorrectionResult(
                original_grid=grid,
                corrected_grid=grid.copy(),
                corrections_applied=[],
                groups_found=[],
            )

        # Find parallel groups
        groups = self._parallel_finder.find_parallel_groups(lines)

        # Calculate corrections for each group
        all_corrections: list[ShiftCorrection] = []
        for group in groups:
            alignment_result = self._alignment_calculator.calculate_alignment(group)
            all_corrections.extend(alignment_result.corrections)

        # Apply corrections
        corrected_grid = grid.copy()
        applied_corrections: list[ShiftCorrection] = []

        for correction in all_corrections:
            try:
                corrected_grid = self._shift_corrector.apply_correction(
                    correction, corrected_grid
                )
                applied_corrections.append(correction)
            except ValueError:
                # Skip corrections that would go out of bounds
                pass

        return CorrectionResult(
            original_grid=grid,
            corrected_grid=corrected_grid,
            corrections_applied=applied_corrections,
            groups_found=groups,
        )

    def analyze(self, grid: Grid) -> CorrectionResult:
        """
        Analyze a grid without applying corrections.

        Args:
            grid: Grid to analyze.

        Returns:
            CorrectionResult with corrections that would be applied.
        """
        # Detect lines
        lines = self._line_detector.detect_lines(grid)

        if not lines:
            return CorrectionResult(
                original_grid=grid,
                corrected_grid=grid.copy(),
                corrections_applied=[],
                groups_found=[],
            )

        # Find parallel groups
        groups = self._parallel_finder.find_parallel_groups(lines)

        # Calculate corrections for each group (but don't apply)
        all_corrections: list[ShiftCorrection] = []
        for group in groups:
            alignment_result = self._alignment_calculator.calculate_alignment(group)
            all_corrections.extend(alignment_result.corrections)

        return CorrectionResult(
            original_grid=grid,
            corrected_grid=grid.copy(),  # Unchanged
            corrections_applied=all_corrections,  # What would be applied
            groups_found=groups,
        )
