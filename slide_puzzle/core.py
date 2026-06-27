"""Pure Python slide puzzle engine for logic and testing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SlidePuzzle:
    """A simple slide puzzle engine.

    The board is stored as a flat list of tile values, where 0 represents
    the blank space. The puzzle size is the side length of the board.
    """

    size: int
    board: List[int]
    moves: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.size <= 0:
            raise ValueError("size must be positive")
        expected_count = self.size * self.size
        if len(self.board) != expected_count:
            raise ValueError("board length does not match the puzzle size")
        if set(self.board) != set(range(expected_count)):
            raise ValueError("board must contain each value from 0 to size^2 - 1 exactly once")

    @property
    def blank_index(self) -> int:
        return self.board.index(0)

    def is_solved(self) -> bool:
        return self.board == list(range(1, self.size * self.size)) + [0]

    def legal_moves(self) -> List[int]:
        blank = self.blank_index
        row, col = divmod(blank, self.size)
        moves: List[int] = []
        if row > 0:
            moves.append(self.board[blank - self.size])
        if row + 1 < self.size:
            moves.append(self.board[blank + self.size])
        if col > 0:
            moves.append(self.board[blank - 1])
        if col + 1 < self.size:
            moves.append(self.board[blank + 1])
        return sorted(moves)

    def move(self, tile: int) -> bool:
        if tile not in self.board:
            return False
        blank = self.blank_index
        tile_index = self.board.index(tile)
        if abs(tile_index - blank) not in {1, self.size}:
            return False
        self.board[blank], self.board[tile_index] = self.board[tile_index], self.board[blank]
        self.moves += 1
        return True