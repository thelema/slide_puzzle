"""Game engine for the slide puzzle.

Provides the core gameplay logic: sliding shapes, validating moves
through colored edge windows, and detecting win/loss states.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from .core import (
    Board,
    Color,
    Direction,
    Edge,
    PuzzleState,
    Shape,
    SlideResult,
)


# ──────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────


def new_game(board: Board) -> PuzzleState:
    """Create a new mutable PuzzleState from a Board definition."""
    return PuzzleState(
        board=board,
        shapes=[Shape(s.id, list(s.cells), s.color, s.row, s.col) for s in board.shapes],
        removed=[],
    )


def can_slide(state: PuzzleState, shape_id: int, direction: Direction) -> SlideResult:
    """Check whether a shape can slide one cell in *direction*.

    Returns a ``SlideResult`` with *success* and optionally *reason*.
    """
    shape = _find_shape(state.shapes, shape_id)
    if shape is None:
        return SlideResult(False, reason="Shape not found on board")

    dr, dc = direction.value
    new_row, new_col = shape.row + dr, shape.col + dc

    # Projected absolute positions after the slide
    new_occupied: List[Tuple[int, int]] = [
        (new_row + c.row, new_col + c.col) for c in shape.cells
    ]

    # Occupied cells of all OTHER shapes
    other_occupied = _occupied_set(state.shapes)
    for cell in shape.occupied_cells():
        other_occupied.discard(cell)

    for nr, nc in new_occupied:
        if _is_in_bounds(nr, nc, state.board):
            if (nr, nc) in other_occupied:
                return SlideResult(False, reason="Blocked by another shape")
        else:
            # Exiting the board — must pass through a same-colored window.
            old_row, old_col = nr - dr, nc - dc
            if not _exited_through_window(old_row, old_col, nr, nc, shape.color, state.board):
                return SlideResult(False, reason="No matching exit window")

    fully_off = _all_off_board(new_occupied, state.board)
    return SlideResult(True, shape_removed=fully_off)


def execute_slide(state: PuzzleState, shape_id: int, direction: Direction) -> SlideResult:
    """Attempt to slide a shape. Mutates *state* and returns the result.

    If the shape fully exits the board it is moved to ``state.removed``.
    """
    result = can_slide(state, shape_id, direction)
    if not result.success:
        return result

    shape = _find_shape(state.shapes, shape_id)
    assert shape is not None

    dr, dc = direction.value
    shape.row += dr
    shape.col += dc
    state.moves += 1

    if _all_off_board(shape.occupied_cells(), state.board):
        state.shapes.remove(shape)
        state.removed.append(shape)
        result.shape_removed = True

    return result


def legal_moves(state: PuzzleState) -> Dict[int, List[Direction]]:
    """Return a ``{shape_id: [Direction, ...]}`` map of valid slides."""
    result: Dict[int, List[Direction]] = {}
    for shape in state.shapes:
        dirs = [d for d in Direction if can_slide(state, shape.id, d).success]
        result[shape.id] = dirs
    return result


def is_won(state: PuzzleState) -> bool:
    """All shapes have been removed from the board."""
    return len(state.shapes) == 0


# ──────────────────────────────────────────────
#  Internal helpers
# ──────────────────────────────────────────────


def _is_in_bounds(row: int, col: int, board: Board) -> bool:
    return 0 <= row < board.rows and 0 <= col < board.cols


def _occupied_set(shapes: List[Shape]) -> Set[Tuple[int, int]]:
    occ: Set[Tuple[int, int]] = set()
    for s in shapes:
        occ.update(s.occupied_cells())
    return occ


def _all_off_board(positions: List[Tuple[int, int]], board: Board) -> bool:
    return all(not _is_in_bounds(r, c, board) for r, c in positions)


def _exited_through_window(
    old_row: int, old_col: int,
    new_row: int, new_col: int,
    shape_color: Color,
    board: Board,
) -> bool:
    """Confirm an off-board move crossed a same-colored edge window."""
    if new_row < 0:
        edge, pos = Edge.TOP, old_col
    elif new_row >= board.rows:
        edge, pos = Edge.BOTTOM, old_col
    elif new_col < 0:
        edge, pos = Edge.LEFT, old_row
    elif new_col >= board.cols:
        edge, pos = Edge.RIGHT, old_row
    else:
        return False

    for w in board.windows:
        if w.edge == edge and w.pos == pos and w.color == shape_color:
            return True
    return False


def _find_shape(shapes: List[Shape], shape_id: int) -> Shape | None:
    for s in shapes:
        if s.id == shape_id:
            return s
    return None