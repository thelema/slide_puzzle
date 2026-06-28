"""Pure data structures for the slide puzzle game.

A puzzle consists of a rectangular board with colored windows on its edges
and rectilinear shapes (polyominoes). The player slides shapes toward
same-colored windows to remove them from the board.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


# ──────────────────────────────────────────────
#  Enums
# ──────────────────────────────────────────────


class Color(Enum):
    """Colors that can be assigned to shapes and edge windows."""
    RED = "#e74c3c"
    GREEN = "#2ecc71"
    BLUE = "#3498db"
    YELLOW = "#f1c40f"
    ORANGE = "#e67e22"
    PURPLE = "#9b59b6"
    CYAN = "#1abc9c"
    PINK = "#e84393"


class Direction(Enum):
    """Cardinal slide directions with their (dr, dc) offsets."""
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class Edge(Enum):
    """Board edges that can host exit windows."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


# ──────────────────────────────────────────────
#  Immutable value types
# ──────────────────────────────────────────────


@dataclass(frozen=True)
class Window:
    """A coloured exit portal at a specific position on a board edge.

    For TOP/BOTTOM edges *pos* is the column index; for LEFT/RIGHT it is
    the row index.
    """
    edge: Edge
    pos: int
    color: Color

    def __post_init__(self) -> None:
        if self.pos < 0:
            raise ValueError(f"Window position must be non-negative, got {self.pos}")


@dataclass(frozen=True)
class Cell:
    """A single cell offset inside a shape's footprint (relative to anchor)."""
    row: int
    col: int


# ──────────────────────────────────────────────
#  Shape (mutable: anchor position changes)
# ──────────────────────────────────────────────


@dataclass
class Shape:
    """A rectilinear polyomino piece placed on the board.

    *cells* holds the shape's footprint as relative offsets from the anchor
    position (*row*, *col*). Only the anchor moves during a slide.
    """
    id: int
    cells: List[Cell]
    color: Color
    row: int
    col: int

    def occupied_cells(self) -> List[Tuple[int, int]]:
        """Absolute (row, col) positions occupied by this shape on the board."""
        return [(self.row + c.row, self.col + c.col) for c in self.cells]


# ──────────────────────────────────────────────
#  Board definition (immutable puzzle layout)
# ──────────────────────────────────────────────


@dataclass(frozen=True)
class Board:
    """A complete puzzle board definition.

    Defines the grid dimensions, the edge windows, and the initial placement
    of every shape.
    """
    rows: int
    cols: int
    windows: List[Window]
    shapes: List[Shape]
    name: str = ""

    def __post_init__(self) -> None:
        if self.rows <= 0:
            raise ValueError(f"Board rows must be positive, got {self.rows}")
        if self.cols <= 0:
            raise ValueError(f"Board cols must be positive, got {self.cols}")


# ──────────────────────────────────────────────
#  Mutable game state
# ──────────────────────────────────────────────


@dataclass
class PuzzleState:
    """Mutable snapshot of a puzzle in progress."""
    board: Board
    shapes: List[Shape]      # shapes still on the board
    removed: List[Shape]     # shapes that have successfully exited
    moves: int = field(default=0, init=False)


# ──────────────────────────────────────────────
#  Slide result
# ──────────────────────────────────────────────


@dataclass
class SlideResult:
    """Outcome of attempting a slide move."""
    success: bool
    shape_removed: bool = False
    reason: str = ""


# ──────────────────────────────────────────────
#  Predefined shape footprints
# ──────────────────────────────────────────────

#: Common polyomino footprints (relative cell offsets).
SHAPE_FOOTPRINTS: dict[str, List[Cell]] = {
    "monomino":         [Cell(0, 0)],
    "domino_h":         [Cell(0, 0), Cell(0, 1)],
    "domino_v":         [Cell(0, 0), Cell(1, 0)],
    "tromino_i":        [Cell(0, 0), Cell(0, 1), Cell(0, 2)],
    "tromino_l":        [Cell(0, 0), Cell(1, 0), Cell(1, 1)],
    "tetromino_o":      [Cell(0, 0), Cell(0, 1), Cell(1, 0), Cell(1, 1)],
    "tetromino_i":      [Cell(0, 0), Cell(0, 1), Cell(0, 2), Cell(0, 3)],
    "tetromino_t":      [Cell(0, 0), Cell(0, 1), Cell(0, 2), Cell(1, 1)],
    "tetromino_l":      [Cell(0, 0), Cell(1, 0), Cell(2, 0), Cell(2, 1)],
    "tetromino_s":      [Cell(0, 1), Cell(0, 2), Cell(1, 0), Cell(1, 1)],
}

# ──────────────────────────────────────────────
#  Demo puzzles
# ──────────────────────────────────────────────


def puzzle_demo_simple() -> Board:
    """A small 3x4 demo puzzle with three monominoes, each near its exit.

    Every shape is a monomino placed adjacent to a same-colored window
    so each can exit in one slide.
    """
    return Board(
        rows=3,
        cols=4,
        name="Demo Simple",
        windows=[
            Window(Edge.TOP, 0, Color.RED),
            Window(Edge.RIGHT, 1, Color.BLUE),
            Window(Edge.BOTTOM, 2, Color.GREEN),
        ],
        shapes=[
            Shape(0, SHAPE_FOOTPRINTS["monomino"], Color.RED, 0, 0),
            Shape(1, SHAPE_FOOTPRINTS["monomino"], Color.BLUE, 1, 3),
            Shape(2, SHAPE_FOOTPRINTS["monomino"], Color.GREEN, 2, 2),
        ],
    )


def puzzle_cross() -> Board:
    """A 5x5 puzzle with four monominoes at the cardinal arms.

    Each shape slides straight toward its same-colored window.
    """
    return Board(
        rows=5,
        cols=5,
        name="Cross",
        windows=[
            Window(Edge.TOP, 2, Color.RED),
            Window(Edge.RIGHT, 2, Color.BLUE),
            Window(Edge.BOTTOM, 2, Color.GREEN),
            Window(Edge.LEFT, 2, Color.YELLOW),
        ],
        shapes=[
            Shape(0, SHAPE_FOOTPRINTS["monomino"], Color.RED, 0, 2),
            Shape(1, SHAPE_FOOTPRINTS["monomino"], Color.BLUE, 2, 4),
            Shape(2, SHAPE_FOOTPRINTS["monomino"], Color.GREEN, 4, 2),
            Shape(3, SHAPE_FOOTPRINTS["monomino"], Color.YELLOW, 2, 0),
        ],
    )


_ALL_PUZZLES: list[Board] = [puzzle_demo_simple(), puzzle_cross()]


def all_puzzles() -> list[Board]:
    """Return all predefined puzzle boards."""
    return list(_ALL_PUZZLES)


def get_puzzle(name: str) -> Optional[Board]:
    """Look up a puzzle board by name (case-insensitive)."""
    for p in _ALL_PUZZLES:
        if p.name.lower() == name.lower():
            return p
    return None