# Slide Puzzle

A classic sliding puzzle game with a Qt Quick UI and a pure-Python game engine.

## Project structure

```
slide_puzzle/
├── main.py                       # Qt Quick entry point
├── slide_puzzle/
│   ├── __init__.py               # Package init
│   ├── core.py                   # Pure Python engine (dataclass)
│   ├── qmladapter.py             # QML-facing QObject wrapper
│   └── qml/
│       └── main.qml              # Qt Quick UI
└── tests/
    └── test_engine.py            # Unit tests
```

## Engine (`slide_puzzle/core.py`)

- `SlidePuzzle` dataclass with `size`, `board` (flat `list[int]`, `0` = blank), and `moves` counter.
- `is_solved()` — checks if the board is in solved order `[1, 2, 3, …, 0]`.
- `legal_moves()` — returns the tile values adjacent to the blank.
- `move(tile)` — swaps the tile with the blank if they are adjacent, increments the move count, and returns `True` / `False`.

## QML adapter (`slide_puzzle/qmladapter.py`)

- `PuzzleAdapter(QObject)` wraps the core dataclass and exposes `board`, `size`, and `moves` as writable Qt `Property`s.
- Exposes `move()`, `reset()`, `legalMoves()`, and `isSolved()` as `@Slot`s callable from QML.
- Emits `boardChanged`, `movesChanged`, and `sizeChanged` signals for reactive UI updates.

## Visualizer (`slide_puzzle/qml/main.qml`)

- A 3×3 grid of tiles rendered from the puzzle board state.
- Click a tile to slide it into the blank.
- "New Game" button shuffles via 100 random legal moves.
- Move counter displayed below the grid.

## Running

```bash
cd slide_puzzle

# Launch the Qt Quick window
uv run python main.py

# Run the test suite
uv run pytest tests/ -v
```

## Requirements

- Python ≥ 3.14
- PySide6
- pytest (for running tests)