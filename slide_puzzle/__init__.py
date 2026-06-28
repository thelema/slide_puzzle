"""Slide puzzle package."""

from .core import (
    Board,
    Cell,
    Color,
    Direction,
    Edge,
    PuzzleState,
    Shape,
    SlideResult,
    Window,
    all_puzzles,
    get_puzzle,
    puzzle_cross,
    puzzle_demo_simple,
)
from .engine import can_slide, execute_slide, is_won, legal_moves, new_game, solve

__all__ = [
    "Board",
    "Cell",
    "Color",
    "Direction",
    "Edge",
    "PuzzleState",
    "Shape",
    "SlideResult",
    "Window",
    "all_puzzles",
    "get_puzzle",
    "puzzle_cross",
    "puzzle_demo_simple",
    "can_slide",
    "execute_slide",
    "is_won",
    "legal_moves",
    "new_game",
]