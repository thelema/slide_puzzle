"""Game engine for the slide puzzle.

Provides the core gameplay logic: sliding shapes, validating moves
through colored edge windows, and detecting win/loss states.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
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
#  Solver (BFS)
# ──────────────────────────────────────────────


@dataclass(frozen=True)
class _SolverState:
    """Canonical, hashable snapshot of which shapes remain and where.

    Each entry is a ``(shape_id, row, col)`` tuple, sorted by shape_id.
    Shapes not present are considered removed.
    """
    placements: Tuple[Tuple[int, int, int], ...]

    @staticmethod
    def from_puzzle_state(state: PuzzleState) -> _SolverState:
        return _SolverState(
            placements=tuple(
                sorted(
                    (s.id, s.row, s.col) for s in state.shapes
                ),
            ),
        )

    def to_puzzle_state(self, board: Board) -> PuzzleState:
        """Reconstruct a mutable PuzzleState from this solver state."""
        shapes: List[Shape] = []
        all_shape_defs = {s.id: s for s in board.shapes}
        for sid, row, col in self.placements:
            proto = all_shape_defs[sid]
            shapes.append(Shape(sid, list(proto.cells), proto.color, row, col))
        removed = [s for s in board.shapes if s.id not in {p[0] for p in self.placements}]
        return PuzzleState(board=board, shapes=shapes, removed=list(removed))


@dataclass
class Solution:
    """A sequence of moves that solves the puzzle."""
    moves: List[Tuple[int, Direction]] = field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.moves)


def solve(board: Board) -> Solution:
    """Find a shortest solution for the given *board* via BFS.

    Returns a ``Solution`` with the move sequence.

    Raises ``ValueError`` if no solution exists.
    """
    initial = new_game(board)
    start = _SolverState.from_puzzle_state(initial)

    if is_won(initial):
        return Solution()

    queue: deque[Tuple[_SolverState, List[Tuple[int, Direction]]]] = deque()
    queue.append((start, []))
    visited: Set[_SolverState] = {start}

    while queue:
        state, path = queue.popleft()
        ps = state.to_puzzle_state(board)

        for shape_id, dirs in legal_moves(ps).items():
            for direction in dirs:
                # Clone the state, apply the move
                child_ps = state.to_puzzle_state(board)
                execute_slide(child_ps, shape_id, direction)
                child = _SolverState.from_puzzle_state(child_ps)

                if child not in visited:
                    new_path = path + [(shape_id, direction)]
                    if is_won(child_ps):
                        return Solution(moves=new_path)
                    visited.add(child)
                    queue.append((child, new_path))

    raise ValueError("No solution exists for this puzzle")


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