"""Correction engine orchestrating the full correction pipeline."""

from ascii_corrector.config import Settings
from ascii_corrector.correction.alignment_calculator import AlignmentCalculator
from ascii_corrector.correction.box_alignment_calculator import BoxAlignmentCalculator
from ascii_corrector.correction.protocols import CorrectionResult, ShiftCorrection
from ascii_corrector.correction.row_shift_corrector import RowShiftCorrector
from ascii_corrector.correction.shift_corrector import ShiftCorrector
from ascii_corrector.correction.stray_character_finder import StrayCharacterFinder
from ascii_corrector.detection import LineDetector, ParallelGroup, ParallelLineFinder
from ascii_corrector.detection.box_detector import BoxDetector
from ascii_corrector.detection.structure_classifier import StructureClassifier, StructureType
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
        settings: Settings | None = None,
    ) -> None:
        """
        Initialize the correction engine.

        Args:
            tolerance: Position tolerance for parallel line grouping.
            min_line_length: Minimum characters to consider a line.
            min_overlap_ratio: Minimum overlap ratio for parallel detection.
            settings: Application settings (uses defaults if None).
        """
        self._tolerance = tolerance
        self._min_line_length = min_line_length
        self._min_overlap_ratio = min_overlap_ratio
        self._settings = settings or Settings()

        # Initialize components
        self._line_detector = LineDetector(min_line_length=min_line_length)
        self._parallel_finder = ParallelLineFinder(
            tolerance=tolerance,
            min_overlap_ratio=min_overlap_ratio,
        )
        self._alignment_calculator = AlignmentCalculator()
        self._box_detector = BoxDetector(min_size=2)
        self._box_alignment_calculator = BoxAlignmentCalculator(tolerance=tolerance)
        self._structure_classifier = StructureClassifier(tree_branch_threshold=2)
        self._shift_corrector = ShiftCorrector()
        self._stray_finder = StrayCharacterFinder(tolerance=tolerance)
        self._row_shift_corrector = RowShiftCorrector(tolerance=tolerance)

    def correct(self, grid: Grid) -> CorrectionResult:
        """
        Apply all corrections to a grid.

        Pipeline:
        1. Detect lines in the grid
        2. Find parallel line groups
        3. Calculate alignment corrections for each group
        4. Detect and align box structures
        5. Find and correct stray characters
        6. Detect and correct row shifts
        7. Apply all corrections

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

        # Classify structure type to detect trees
        structure_type = self._structure_classifier.classify(grid)

        # Filter parallel groups to preserve tree branch patterns
        if structure_type == StructureType.TREE and self._settings.preserve_trees:
            groups = self._filter_tree_groups(groups, grid)

        # Calculate corrections for each group
        all_corrections: list[ShiftCorrection] = []
        for group in groups:
            alignment_result = self._alignment_calculator.calculate_alignment(group)
            all_corrections.extend(alignment_result.corrections)

        # Detect and align box structures (large boxes beyond tolerance)
        boxes = self._box_detector.detect_boxes(grid)
        box_corrections = self._box_alignment_calculator.calculate_corrections(boxes)
        all_corrections.extend(box_corrections)

        # Find stray character corrections
        stray_corrections = self._stray_finder.find_stray_corrections(grid, lines)
        all_corrections.extend(stray_corrections)

        # Find whole-row shift corrections (column consensus)
        row_shift_corrections = self._row_shift_corrector.find_row_shift_corrections(
            grid
        )
        all_corrections.extend(row_shift_corrections)

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

        # Classify structure type to detect trees
        structure_type = self._structure_classifier.classify(grid)

        # Filter parallel groups to preserve tree branch patterns
        if structure_type == StructureType.TREE and self._settings.preserve_trees:
            groups = self._filter_tree_groups(groups, grid)

        # Calculate corrections for each group (but don't apply)
        all_corrections: list[ShiftCorrection] = []
        for group in groups:
            alignment_result = self._alignment_calculator.calculate_alignment(group)
            all_corrections.extend(alignment_result.corrections)

        # Detect and align box structures (large boxes beyond tolerance)
        boxes = self._box_detector.detect_boxes(grid)
        box_corrections = self._box_alignment_calculator.calculate_corrections(boxes)
        all_corrections.extend(box_corrections)

        # Find stray character corrections
        stray_corrections = self._stray_finder.find_stray_corrections(grid, lines)
        all_corrections.extend(stray_corrections)

        # Find whole-row shift corrections (column consensus)
        row_shift_corrections = self._row_shift_corrector.find_row_shift_corrections(
            grid
        )
        all_corrections.extend(row_shift_corrections)

        return CorrectionResult(
            original_grid=grid,
            corrected_grid=grid.copy(),  # Unchanged
            corrections_applied=all_corrections,  # What would be applied
            groups_found=groups,
        )

    def _filter_tree_groups(
        self, groups: list[ParallelGroup], grid: Grid
    ) -> list[ParallelGroup]:
        """Filter out parallel groups that would break tree branch patterns.

        Tree branches (e.g., +-- notation) should not be aligned with other
        horizontal lines as that would break the tree structure.

        Args:
            groups: Parallel groups found by ParallelLineFinder.
            grid: Grid to check for tree patterns.

        Returns:
            Filtered list of groups excluding those with tree branches.
        """
        filtered = []
        for group in groups:
            if not self._group_contains_tree_branch(group, grid):
                filtered.append(group)
        return filtered

    def _group_contains_tree_branch(
        self, group: ParallelGroup, grid: Grid
    ) -> bool:
        """Check if any line in the group is part of a tree branch pattern.

        Args:
            group: Parallel group to check.
            grid: Grid to scan.

        Returns:
            True if group contains tree branch notation.
        """
        for line in group.lines:
            # Check if any cell in the line is part of a tree branch
            for cell in line.cells:
                if self._structure_classifier._is_tree_branch(grid, cell.position):
                    return True
        return False
