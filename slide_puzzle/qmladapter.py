"""Qt QML adapter for the slide puzzle engine.

Wraps the pure SlidePuzzle dataclass in a QObject so it can be
registered and used from QML.
"""

from __future__ import annotations

from typing import List
from PySide6.QtCore import QObject, Property, Signal, Slot

from .core import SlidePuzzle as CoreSlidePuzzle


class PuzzleAdapter(QObject):
    """QML-facing adapter around CoreSlidePuzzle."""

    boardChanged = Signal(list)
    movesChanged = Signal(int)
    sizeChanged = Signal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._size = 3
        self._board = list(range(1, 9)) + [0]
        self._puzzle = CoreSlidePuzzle(size=self._size, board=self._board)

    # --- Qt properties (readable from QML, board/size writable for initialisation) ---

    def _get_size(self) -> int:
        return self._puzzle.size

    def _set_size(self, value: int) -> None:
        self._size = value
        self._rebuild()

    size = Property(int, _get_size, _set_size, notify=sizeChanged)

    def _get_board(self) -> List[int]:
        return self._puzzle.board

    def _set_board(self, value: List[int]) -> None:
        self._board = value
        self._rebuild()

    board = Property(list, _get_board, _set_board, notify=boardChanged)

    def _get_moves(self) -> int:
        return self._puzzle.moves

    moves = Property(int, _get_moves, notify=movesChanged)

    # --- Internal ---

    def _rebuild(self) -> None:
        self._puzzle = CoreSlidePuzzle(size=self._size, board=self._board)
        self.sizeChanged.emit(self._size)
        self.boardChanged.emit(self._board)
        self.movesChanged.emit(self._puzzle.moves)

    # --- QML slots ---
    @Slot(int, result=bool)
    def move(self, tile: int) -> bool:
        result = self._puzzle.move(tile)
        if result:
            self.boardChanged.emit(self._puzzle.board)
            self.movesChanged.emit(self._puzzle.moves)
        return result

    @Slot()
    def reset(self) -> None:
        self._board = list(range(1, self._size * self._size)) + [0]
        self._puzzle = CoreSlidePuzzle(size=self._size, board=self._board)
        self.boardChanged.emit(self._board)
        self.movesChanged.emit(self._puzzle.moves)

    @Slot(result=list)
    def legalMoves(self) -> list:
        return self._puzzle.legal_moves()

    @Slot(result=bool)
    def isSolved(self) -> bool:
        return self._puzzle.is_solved()