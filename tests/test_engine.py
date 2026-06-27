import unittest
from slide_puzzle.engine import SlidePuzzle


class TestSlidePuzzle(unittest.TestCase):
    def test_initialization(self):
        # Test a solved 2x2 puzzle
        puzzle = SlidePuzzle(size=2, board=[1, 2, 3, 0])
        self.assertEqual(puzzle.size, 2)
        self.assertEqual(puzzle.board, [1, 2, 3, 0])
        self.assertEqual(puzzle.blank_index, 3)
        self.assertTrue(puzzle.is_solved())

    def test_legal_moves(self):
        # Test legal moves for a 2x2 puzzle with blank at index 3 (bottom right)
        puzzle = SlidePuzzle(size=2, board=[1, 2, 3, 0])
        # Blank at (1,1) -> up (tile 2 at index 1), left (tile 3 at index 2)
        self.assertCountEqual(puzzle.legal_moves(), [2, 3])

        # Test legal moves for a 3x3 puzzle with blank at center (index 4)
        puzzle = SlidePuzzle(size=3, board=[1, 2, 3, 4, 0, 5, 6, 7, 8])
        # Blank at (1,1) -> up (2), down (7), left (4), right (5)
        self.assertCountEqual(puzzle.legal_moves(), [2, 4, 5, 7])

    def test_move(self):
        puzzle = SlidePuzzle(size=2, board=[1, 2, 3, 0])
        # blank at index 3. Tile 3 (index 2) is left-adjacent -> succeeds
        self.assertTrue(puzzle.move(3))
        self.assertEqual(puzzle.board, [1, 2, 0, 3])
        self.assertEqual(puzzle.blank_index, 2)
        self.assertEqual(puzzle.moves, 1)

        # Tile 2 (now at index 1) is above blank (index 2) -> also adjacent
        self.assertTrue(puzzle.move(2))
        self.assertEqual(puzzle.board, [1, 0, 2, 3])
        self.assertEqual(puzzle.blank_index, 1)
        self.assertEqual(puzzle.moves, 2)

    def test_move_non_adjacent_fails(self):
        # Tile 1 (index 0) is diagonal to blank (index 3) in a 2x2, not adjacent
        puzzle = SlidePuzzle(size=2, board=[1, 2, 3, 0])
        self.assertFalse(puzzle.move(1))
        self.assertEqual(puzzle.board, [1, 2, 3, 0])
        self.assertEqual(puzzle.moves, 0)

    def test_is_solved(self):
        # Test solved state
        puzzle = SlidePuzzle(size=3, board=[1, 2, 3, 4, 5, 6, 7, 8, 0])
        self.assertTrue(puzzle.is_solved())

        # Test unsolved state
        puzzle = SlidePuzzle(size=3, board=[1, 2, 3, 4, 5, 6, 7, 0, 8])
        self.assertFalse(puzzle.is_solved())


if __name__ == "__main__":
    unittest.main()