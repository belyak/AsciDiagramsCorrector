"""Enumerations for ASCII diagram domain."""

from enum import Enum, auto


class CharacterClass(Enum):
    """Classification of ASCII characters for diagram parsing."""

    HORIZONTAL = auto()  # -, =, _, ─, ━, ═
    VERTICAL = auto()  # |, !, │, ┃, ║
    CORNER = auto()  # +, ., ', `, ┌, ┐, └, ┘, ╔, ╗, ╚, ╝, etc
    JUNCTION = auto()  # *, ┼, ├, ┤, ┬, ┴, ╋
    DIAGONAL_DOWN = auto()  # \, ╲
    DIAGONAL_UP = auto()  # /, ╱
    ARROW = auto()  # <, >, ^, v, V
    TEXT = auto()  # alphanumeric
    WHITESPACE = auto()  # space, tab
    UNKNOWN = auto()  # other


class Direction(Enum):
    """Direction of line traversal."""

    HORIZONTAL = auto()
    VERTICAL = auto()
    DIAGONAL_DOWN = auto()
    DIAGONAL_UP = auto()


class LineType(Enum):
    """Type of detected line."""

    HORIZONTAL = auto()
    VERTICAL = auto()
    BOX_TOP = auto()
    BOX_BOTTOM = auto()
    BOX_LEFT = auto()
    BOX_RIGHT = auto()
    CONNECTOR = auto()
    UNKNOWN = auto()
