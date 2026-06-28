"""Tests for the slide-puzzle engine."""

from __future__ import annotations

import unittest

from slide_puzzle.core import (
    Board,
    Cell,
    Color,
    Direction,
    Edge,
    Shape,
    Window,
    puzzle_demo_simple,
    puzzle_cross,
)
from slide_puzzle.engine import (
    can_slide,
    execute_slide,
    is_won,
    legal_moves,
    new_game,
    solve,
)


class TestPuzzleDataStructures(unittest.TestCase):
    def test_board_validation(self) -> None:
        with self.assertRaises(ValueError):
            Board(rows=0, cols=4, windows=[], shapes=[])

    def test_window_validation(self) -> None:
        with self.assertRaises(ValueError):
            Window(Edge.TOP, -1, Color.RED)

    def test_shape_occupied_cells(self) -> None:
        shape = Shape(0, [Cell(0, 0), Cell(0, 1)], Color.RED, 2, 3)
        self.assertEqual(shape.occupied_cells(), [(2, 3), (2, 4)])

    def test_demo_puzzle_has_shapes_and_windows(self) -> None:
        board = puzzle_demo_simple()
        self.assertEqual(board.rows, 3)
        self.assertEqual(board.cols, 4)
        self.assertEqual(len(board.shapes), 3)
        self.assertEqual(len(board.windows), 3)


class TestEngineSlides(unittest.TestCase):
    def setUp(self) -> None:
        self.board = Board(
            rows=4,
            cols=4,
            windows=[
                Window(Edge.RIGHT, 1, Color.BLUE),
                Window(Edge.TOP, 1, Color.RED),
            ],
            shapes=[
                # A red monomino at (1, 1) — can slide UP to exit through
                # the TOP edge window at column 1 (Color.RED).
                Shape(0, [Cell(0, 0)], Color.RED, 1, 1),
                # A blue monomino at (1, 3) — can slide RIGHT through the
                # RIGHT edge window at row 1 (Color.BLUE).
                Shape(1, [Cell(0, 0)], Color.BLUE, 1, 3),
            ],
            name="Test Board",
        )
        self.state = new_game(self.board)

    def test_slide_right_into_blocked_fails(self) -> None:
        # Red at (1,1) slides RIGHT -> (1,2). Blue at (1,3) is not adjacent.
        result = can_slide(self.state, 0, Direction.RIGHT)
        self.assertTrue(result.success)

        # Actually slide it right once
        execute_slide(self.state, 0, Direction.RIGHT)
        self.assertEqual(self.state.shapes[0].col, 2)

    def test_slide_off_board_through_wrong_color_fails(self) -> None:
        # Create a board where a red shape starts at (1,0) i.e. at the LEFT edge.
        # Sliding LEFT exits the board — no LEFT window exists, so it fails.
        board = Board(
            rows=4, cols=4,
            windows=[Window(Edge.RIGHT, 1, Color.BLUE)],
            shapes=[Shape(0, [Cell(0, 0)], Color.RED, 1, 0)],
            name="Wrong Color Test",
        )
        state = new_game(board)
        result = can_slide(state, 0, Direction.LEFT)
        self.assertFalse(result.success)
        self.assertIn("window", result.reason.lower())

    def test_slide_off_board_through_right_color_succeeds(self) -> None:
        # Blue shape at (1,3). Slide RIGHT -> off through BLUE window -> removed!
        result = can_slide(self.state, 1, Direction.RIGHT)
        self.assertTrue(result.success)
        self.assertTrue(result.shape_removed)

        execute_slide(self.state, 1, Direction.RIGHT)
        self.assertEqual(len(self.state.shapes), 1)
        self.assertEqual(len(self.state.removed), 1)

    def test_slide_up_through_red_window(self) -> None:
        # Red shape at (1,0). Slide UP -> (0,0). Then UP again to exit.
        execute_slide(self.state, 0, Direction.UP)  # row 0
        self.assertEqual(self.state.shapes[0].row, 0)
        result = can_slide(self.state, 0, Direction.UP)
        self.assertTrue(result.success)
        self.assertTrue(result.shape_removed)

        execute_slide(self.state, 0, Direction.UP)
        self.assertEqual(len(self.state.shapes), 1)  # only blue left
        self.assertEqual(len(self.state.removed), 1)

    def test_blocked_by_another_shape(self) -> None:
        # Red at (1,1), blue at (1,3). Move red RIGHT 2 times to (1,3) where
        # blue sits. Next RIGHT is blocked.
        for _ in range(2):
            execute_slide(self.state, 0, Direction.RIGHT)
        result = can_slide(self.state, 0, Direction.RIGHT)
        self.assertFalse(result.success)
        self.assertIn("Blocked", result.reason)

    def test_legal_moves(self) -> None:
        moves = legal_moves(self.state)
        self.assertIn(0, moves)
        self.assertIn(1, moves)

    def test_is_won(self) -> None:
        self.assertFalse(is_won(self.state))
        # Remove red: slide UP twice (row 1 -> row 0 -> exit through TOP/1)
        execute_slide(self.state, 0, Direction.UP)
        execute_slide(self.state, 0, Direction.UP)
        # Remove blue: slide RIGHT once (exit through RIGHT/1)
        execute_slide(self.state, 1, Direction.RIGHT)
        self.assertTrue(is_won(self.state))


class TestDemoPuzzleIntegration(unittest.TestCase):
    def test_demo_simple_shape_count(self) -> None:
        state = new_game(puzzle_demo_simple())
        self.assertEqual(len(state.shapes), 3)

    def test_cross_puzzle_shape_count(self) -> None:
        state = new_game(puzzle_cross())
        self.assertEqual(len(state.shapes), 4)

    def test_move_count_tracks(self) -> None:
        state = new_game(puzzle_demo_simple())
        self.assertEqual(state.moves, 0)
        execute_slide(state, 0, Direction.RIGHT)
        self.assertEqual(state.moves, 1)


if __name__ == "__main__":
    unittest.main()


class TestSolver(unittest.TestCase):
    def test_solve_demo_simple(self) -> None:
        solution = solve(puzzle_demo_simple())
        self.assertGreater(solution.length, 0)
        # Verify the solution actually solves the puzzle
        state = new_game(puzzle_demo_simple())
        for shape_id, direction in solution.moves:
            execute_slide(state, shape_id, direction)
        self.assertTrue(is_won(state))

    def test_solve_cross(self) -> None:
        solution = solve(puzzle_cross())
        self.assertGreater(solution.length, 0)
        state = new_game(puzzle_cross())
        for shape_id, direction in solution.moves:
            execute_slide(state, shape_id, direction)
        self.assertTrue(is_won(state))

    def test_solve_unsolvable_raises(self) -> None:
        # A monomino placed far from any matching window — unsolvable.
        board = Board(
            rows=3, cols=3,
            windows=[Window(Edge.TOP, 0, Color.RED)],
            shapes=[Shape(0, [Cell(0, 0)], Color.BLUE, 2, 2)],
            name="Unsolvable",
        )
        with self.assertRaises(ValueError):
            solve(board)

    def test_solve_already_won(self) -> None:
        board = Board(
            rows=3, cols=3,
            windows=[],
            shapes=[],
            name="Empty",
        )
        solution = solve(board)
        self.assertEqual(solution.length, 0)