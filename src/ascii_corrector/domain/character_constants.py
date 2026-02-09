"""Central character classification constants for ASCII and Unicode characters."""

# ============================================================================
# ASCII Characters
# ============================================================================

# ASCII horizontal line characters
ASCII_HORIZONTAL = frozenset({"-", "=", "_"})

# ASCII vertical line characters
ASCII_VERTICAL = frozenset({"|", "!"})

# ASCII corner characters (box corners)
ASCII_CORNER = frozenset({"+", ".", "'", "`"})

# ASCII junction characters (cross, T-junction, etc)
ASCII_JUNCTION = frozenset({"*"})

# ASCII arrow characters
ASCII_ARROW = frozenset({"<", ">", "^", "v", "V"})

# ASCII bridge characters (connect line segments, e.g., + bridges horizontal lines)
ASCII_BRIDGE = frozenset({"+", "."})

# ============================================================================
# Unicode Box-Drawing Characters
# ============================================================================

# Unicode horizontal line characters (light, heavy, double)
UNICODE_HORIZONTAL = frozenset({
    "\u2500",  # ─ LIGHT HORIZONTAL
    "\u2501",  # ━ HEAVY HORIZONTAL
    "\u2550",  # ═ DOUBLE HORIZONTAL
})

# Unicode vertical line characters (light, heavy, double)
UNICODE_VERTICAL = frozenset({
    "\u2502",  # │ LIGHT VERTICAL
    "\u2503",  # ┃ HEAVY VERTICAL
    "\u2551",  # ║ DOUBLE VERTICAL
})

# Unicode corner characters (pure corners - 4 corners only)
UNICODE_CORNER = frozenset({
    "\u250C",  # ┌ LIGHT DOWN AND RIGHT
    "\u2510",  # ┐ LIGHT DOWN AND LEFT
    "\u2514",  # └ LIGHT UP AND RIGHT
    "\u2518",  # ┘ LIGHT UP AND LEFT
    "\u250F",  # ┏ HEAVY DOWN AND RIGHT
    "\u2513",  # ┓ HEAVY DOWN AND LEFT
    "\u2517",  # ┗ HEAVY UP AND RIGHT
    "\u251B",  # ┛ HEAVY UP AND LEFT
    "\u2554",  # ╔ DOUBLE DOWN AND RIGHT
    "\u2557",  # ╗ DOUBLE DOWN AND LEFT
    "\u255A",  # ╚ DOUBLE UP AND RIGHT
    "\u255D",  # ╝ DOUBLE UP AND LEFT
})

# Unicode junction characters (T-junctions, crosses)
UNICODE_JUNCTION = frozenset({
    "\u251C",  # ├ LIGHT VERTICAL AND RIGHT
    "\u2524",  # ┤ LIGHT VERTICAL AND LEFT
    "\u252C",  # ┬ LIGHT DOWN AND HORIZONTAL
    "\u2534",  # ┴ LIGHT UP AND HORIZONTAL
    "\u253C",  # ┼ LIGHT VERTICAL AND HORIZONTAL
    "\u2520",  # ┠ HEAVY VERTICAL AND RIGHT
    "\u2528",  # ┨ HEAVY VERTICAL AND LEFT
    "\u252F",  # ┯ HEAVY DOWN AND HORIZONTAL
    "\u2537",  # ┷ HEAVY UP AND HORIZONTAL
    "\u253F",  # ┿ HEAVY VERTICAL AND HORIZONTAL
    "\u254B",  # ╋ HEAVY VERTICAL AND HORIZONTAL
})

# Unicode bridge characters (can bridge line segments)
UNICODE_BRIDGE = UNICODE_CORNER | UNICODE_JUNCTION

# ============================================================================
# Diagonal Characters
# ============================================================================

# Diagonal down characters (top-left to bottom-right)
DIAGONAL_DOWN = frozenset({
    "\\",
    "\u2572",  # ╲ BOX DRAWINGS LIGHT DIAGONAL
})

# Diagonal up characters (bottom-left to top-right)
DIAGONAL_UP = frozenset({
    "/",
    "\u2571",  # ╱ BOX DRAWINGS LIGHT DIAGONAL
})

# ============================================================================
# Combined Character Sets
# ============================================================================

# All horizontal line characters (ASCII + Unicode)
HORIZONTAL_CHARS = ASCII_HORIZONTAL | UNICODE_HORIZONTAL

# All vertical line characters (ASCII + Unicode)
VERTICAL_CHARS = ASCII_VERTICAL | UNICODE_VERTICAL

# All corner characters (ASCII + Unicode)
CORNER_CHARS = ASCII_CORNER | UNICODE_CORNER

# All junction characters (ASCII + Unicode)
JUNCTION_CHARS = ASCII_JUNCTION | UNICODE_JUNCTION

# All bridge characters (for line detection)
BRIDGE_CHARS = ASCII_BRIDGE | UNICODE_BRIDGE

# All diagonal characters
ALL_DIAGONAL = DIAGONAL_DOWN | DIAGONAL_UP

# Structural characters used for alignment (vertical + corner + junction)
STRUCTURAL_CHARS = VERTICAL_CHARS | CORNER_CHARS | JUNCTION_CHARS

# All line characters (horizontal + vertical + diagonal + corner + junction)
ALL_LINE_CHARS = HORIZONTAL_CHARS | VERTICAL_CHARS | CORNER_CHARS | JUNCTION_CHARS | ALL_DIAGONAL

# Arrow characters
ARROW_CHARS = ASCII_ARROW

# Whitespace characters
WHITESPACE_CHARS = frozenset({" ", "\t"})
