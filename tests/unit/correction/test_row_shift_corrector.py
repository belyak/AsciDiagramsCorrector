"""Unit tests for RowShiftCorrector."""

import pytest

from ascii_corrector.correction.row_shift_corrector import RowShiftCorrector
from ascii_corrector.domain import Direction, Grid


class TestRowShiftCorrectorColumnConsensus:
    """Tests for column consensus detection and whole-row shifting."""

    def test_single_box_shifted_bottom_row(self) -> None:
        """Bottom row shifted right by 1 should be corrected."""
        # The Position box case from ARCHITECTURE.md section 3
        broken = (
            " +--+\n"
            " |  |\n"
            " |  |\n"
            " |  |\n"
            "  +--+"  # shifted right by 1
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1
        assert corrections[0].row_offset == 0

    def test_single_box_shifted_middle_row(self) -> None:
        """Middle row shifted right by 1 should be corrected."""
        broken = (
            " +--+\n"
            " |  |\n"
            "  |  |\n"  # shifted right by 1
            " |  |\n"
            " +--+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_no_correction_when_all_aligned(self) -> None:
        """No corrections for a perfectly aligned box."""
        correct = (
            "+--+\n"
            "|  |\n"
            "|  |\n"
            "+--+"
        )
        grid = Grid.from_string(correct)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 0

    def test_shifted_row_with_text_content(self) -> None:
        """Entire row with text content shifted should be corrected."""
        # Key test: rows with text SHOULD be corrected if ALL structural
        # chars are consistently shifted
        broken = (
            " +------------------+\n"
            " | some text        |\n"
            "  | shifted text     |\n"  # entire row shifted right by 1
            " | more text        |\n"
            " +------------------+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_shifted_row_moves_all_cells(self) -> None:
        """The correction Line should contain ALL non-space cells on the row."""
        broken = (
            " +------+\n"
            " | text |\n"
            "  | text |\n"  # shifted right by 1
            " +------+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        # All non-space cells on row 2 should be in the correction's Line
        row_cells = corrections[0].line.cells
        # Row 2: "  | text |" -> non-space chars are |, t, e, x, t, |
        non_space_count = sum(
            1 for c in "  | text |" if c != " "
        )
        assert len(row_cells) == non_space_count

    def test_two_side_by_side_boxes_shifted_row(self) -> None:
        """Two boxes side by side with one shifted row should be corrected."""
        broken = (
            " +--+  +--+\n"
            " |  |  |  |\n"
            "  |  |  |  |\n"  # shifted right by 1 — all 4 pipes shifted
            " |  |  |  |\n"
            " +--+  +--+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_no_correction_when_mixed_offsets(self) -> None:
        """No correction when structural chars have different offsets."""
        # Left | at consensus col, right | shifted — NOT a whole-row shift
        broken = (
            "+----+\n"
            "|    |\n"
            "|     |\n"  # right | shifted right, left | correct
            "|    |\n"
            "+----+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 0

    def test_shifted_left_by_one(self) -> None:
        """Row shifted left by 1 should be corrected with positive col_offset."""
        broken = (
            "  +--+\n"
            "  |  |\n"
            " |  |\n"  # shifted left by 1
            "  |  |\n"
            "  +--+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == 1

    def test_no_correction_beyond_tolerance(self) -> None:
        """No correction when shift exceeds tolerance."""
        broken = (
            "+--+\n"
            "|  |\n"
            "   |  |\n"  # shifted right by 3
            "|  |\n"
            "+--+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 0

    def test_tree_structure_shifted_branch(self) -> None:
        """Shifted branch in tree structure should be corrected."""
        # Exception hierarchy-style tree
        broken = (
            "  |\n"
            "  +-- Error1\n"
            "  |\n"
            "   +-- Error2\n"  # shifted right by 1
            "  |\n"
            "  +-- Error3"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_empty_grid(self) -> None:
        """Empty grid should produce no corrections."""
        grid = Grid.from_string("")
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 0

    def test_no_structural_chars(self) -> None:
        """Grid with no structural chars should produce no corrections."""
        grid = Grid.from_string("hello\nworld")
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 0

    def test_single_structural_char_row_with_consensus(self) -> None:
        """Row with a single structural char should still be corrected if consensus exists."""
        # Tree structure: single | on each row
        broken = (
            " |\n"
            " |\n"
            "  |\n"  # shifted right by 1
            " |\n"
            " |"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_multiple_shifted_rows(self) -> None:
        """Multiple shifted rows should each get a correction."""
        broken = (
            " +--+\n"
            "  |  |\n"  # shifted right by 1
            " |  |\n"
            "  |  |\n"  # shifted right by 1
            " +--+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 2
        assert all(c.col_offset == -1 for c in corrections)

    def test_correction_would_go_out_of_bounds_skipped(self) -> None:
        """Correction that would shift cells out of bounds should be skipped."""
        # Row shifted left — correcting it would push content further left past col 0
        # This is a row at the edge where shifting left would go out of bounds
        broken = (
            " +--+\n"
            " |  |\n"
            "|  |\n"  # shifted left by 1 — correcting would need col_offset=+1
            " |  |\n"
            " +--+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        # Should still produce the correction (bounds check is done by ShiftCorrector)
        assert len(corrections) == 1
        assert corrections[0].col_offset == 1


class TestRowShiftCorrectorArchitectureMdPatterns:
    """Tests mimicking actual patterns from ARCHITECTURE.md."""

    def test_position_box_shifted_bottom(self) -> None:
        """Position box from section 3: bottom +--+ shifted right by 1."""
        broken = (
            " +------------------+\n"
            " | Position         |\n"
            " | (frozen)         |\n"
            " |                  |\n"
            " | row: int         |\n"
            " | col: int         |\n"
            " | offset()         |\n"
            " | distance_to()    |\n"
            " | manhattan_dist() |\n"
            "  +------------------+"  # shifted right by 1
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_protocol_box_shifted_row(self) -> None:
        """Protocol box from section 9: one row shifted right by 1."""
        broken = (
            "  +---------------------------+\n"
            "  |                           |\n"
            "  | CharacterClassifierProto  |\n"
            "  | classify(char) -> Class   |\n"
            "  |                           |\n"
            "  | LineDetectorProto         |\n"
            "  | detect_lines(grid)        |\n"
            "   |   -> list[Line]           |\n"  # shifted right by 1
            "  |                           |\n"
            "  +---------------------------+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_settings_table_shifted_row(self) -> None:
        """Settings table from section 10: content row shifted."""
        broken = (
            " +------+\n"
            " | env  |\n"
            " |------|\n"
            " | a: 1 |\n"
            "  | b: 2 |\n"  # shifted right by 1
            " | c: 3 |\n"
            " +------+"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_exception_tree_shifted_branch(self) -> None:
        """Exception tree from section 4: shifted +-- branch."""
        broken = (
            "         |\n"
            "         +-- ConfigurationError\n"
            "         |\n"
            "          +-- DiagramIOError\n"  # shifted right by 1
            "         |\n"
            "         +-- MarkdownParseError"
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1

    def test_correction_result_box_shifted_bottom(self) -> None:
        """CorrectionResult box from section 8: bottom shifted right by 1."""
        broken = (
            " +---------------------+\n"
            " | original_grid: Grid |\n"
            " | corrected_grid: Grid|\n"
            " | corrections_applied |\n"
            " | groups_found        |\n"
            " | corrections_count   |\n"
            "  +---------------------+"  # shifted right by 1
        )
        grid = Grid.from_string(broken)
        corrector = RowShiftCorrector(tolerance=1)

        corrections = corrector.find_row_shift_corrections(grid)

        assert len(corrections) == 1
        assert corrections[0].col_offset == -1
