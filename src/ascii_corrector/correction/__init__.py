"""Correction algorithms for ASCII diagrams."""

from ascii_corrector.correction.alignment_calculator import AlignmentCalculator
from ascii_corrector.correction.correction_engine import CorrectionEngine
from ascii_corrector.correction.protocols import (
    AlignmentResult,
    CorrectionResult,
    ShiftCorrection,
)
from ascii_corrector.correction.shift_corrector import ShiftCorrector

__all__ = [
    "AlignmentCalculator",
    "AlignmentResult",
    "CorrectionEngine",
    "CorrectionResult",
    "ShiftCorrection",
    "ShiftCorrector",
]
