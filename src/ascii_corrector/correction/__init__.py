"""Correction algorithms for ASCII diagrams."""

from ascii_corrector.correction.alignment_calculator import AlignmentCalculator
from ascii_corrector.correction.correction_engine import CorrectionEngine
from ascii_corrector.correction.protocols import (
    AlignmentResult,
    CorrectionResult,
    ShiftCorrection,
)
from ascii_corrector.correction.row_shift_corrector import RowShiftCorrector
from ascii_corrector.correction.shift_corrector import ShiftCorrector
from ascii_corrector.correction.stray_character_finder import StrayCharacterFinder

__all__ = [
    "AlignmentCalculator",
    "AlignmentResult",
    "CorrectionEngine",
    "CorrectionResult",
    "RowShiftCorrector",
    "ShiftCorrection",
    "ShiftCorrector",
    "StrayCharacterFinder",
]
