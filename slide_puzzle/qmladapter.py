"""Qt QML adapter for the slide puzzle engine.

Wraps the puzzle engine data structures in a QObject so they can be
registered and consumed from QML.
"""

from __future__ import annotations

from typing import Any, Dict, List

from PySide6.QtCore import QObject, Property, Signal, Slot

from .core import (
    Board,
    Color,
    Direction,
    Edge,
    PuzzleState,
    Shape,
    Window,
    all_puzzles,
)
from .engine import execute_slide, is_won, legal_moves, new_game


def _color_to_qml(color: Color) -> str:
    return color.value


def _window_to_dict(w: Window) -> Dict[str, Any]:
    return {"edge": w.edge.value, "pos": w.pos, "color": _color_to_qml(w.color)}


def _shape_to_dict(s: Shape) -> Dict[str, Any]:
    cells = [{"row": c.row, "col": c.col} for c in s.cells]
    return {
        "id": s.id,
        "cells": cells,
        "color": _color_to_qml(s.color),
        "row": s.row,
        "col": s.col,
    }


def _direction_to_key(d: Direction) -> str:
    return d.name.lower()


class PuzzleAdapter(QObject):
    """QML-facing adapter around the engine."""

    boardChanged = Signal()
    shapesChanged = Signal()
    removedChanged = Signal()
    movesChanged = Signal(int)
    wonChanged = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._puzzles: List[Board] = all_puzzles()
        self._puzzle_index = 0
        self._state = new_game(self._puzzles[self._puzzle_index])

    # --- Qt readable properties ------------------------------------------------

    def _get_puzzle_names(self) -> List[str]:
        return [p.name for p in self._puzzles]

    puzzleNames = Property(list, _get_puzzle_names, constant=True)

    def _get_board_rows(self) -> int:
        return self._state.board.rows

    boardRows = Property(int, _get_board_rows, constant=True)

    def _get_board_cols(self) -> int:
        return self._state.board.cols

    boardCols = Property(int, _get_board_cols, constant=True)

    def _get_windows(self) -> List[Dict[str, Any]]:
        return [_window_to_dict(w) for w in self._state.board.windows]

    windows = Property("QVariantList", _get_windows, notify=boardChanged)

    def _get_shapes(self) -> List[Dict[str, Any]]:
        return [_shape_to_dict(s) for s in self._state.shapes]

    shapes = Property("QVariantList", _get_shapes, notify=shapesChanged)

    def _get_removed(self) -> List[Dict[str, Any]]:
        return [_shape_to_dict(s) for s in self._state.removed]

    removed = Property("QVariantList", _get_removed, notify=removedChanged)

    def _get_moves(self) -> int:
        return self._state.moves

    moves = Property(int, _get_moves, notify=movesChanged)

    # --- QML-callable slots ----------------------------------------------------

    @Slot(int, str, result=bool)
    def slideShape(self, shape_id: int, direction_str: str) -> bool:
        """Slide a shape by its id and a direction name (up/down/left/right)."""
        try:
            direction = Direction[direction_str.upper()]
        except KeyError:
            return False
        result = execute_slide(self._state, shape_id, direction)
        if result.success:
            self.shapesChanged.emit()
            self.removedChanged.emit()
            self.movesChanged.emit(self._state.moves)
            if is_won(self._state):
                self.wonChanged.emit(True)
        return result.success

    @Slot(int, result="QVariantList")
    def legalMovesFor(self, shape_id: int) -> List[str]:
        """Return list of direction strings a shape can slide."""
        moves = legal_moves(self._state)
        return [_direction_to_key(d) for d in moves.get(shape_id, [])]

    @Slot()
    def reset(self) -> None:
        self._state = new_game(self._puzzles[self._puzzle_index])
        self.boardChanged.emit()
        self.shapesChanged.emit()
        self.removedChanged.emit()
        self.movesChanged.emit(self._state.moves)
        self.wonChanged.emit(False)

    @Slot(int)
    def selectPuzzle(self, index: int) -> None:
        if 0 <= index < len(self._puzzles):
            self._puzzle_index = index
            self.reset()

    @Slot(result=bool)
    def isWon(self) -> bool:
        return is_won(self._state)