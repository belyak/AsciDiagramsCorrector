"""Detection algorithms for ASCII diagrams."""

from ascii_corrector.detection.line_detector import LineDetector
from ascii_corrector.detection.parallel_line_finder import ParallelLineFinder
from ascii_corrector.detection.protocols import ParallelGroup

__all__ = [
    "LineDetector",
    "ParallelGroup",
    "ParallelLineFinder",
]
