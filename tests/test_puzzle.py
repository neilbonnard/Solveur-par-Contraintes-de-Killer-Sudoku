import numpy as np
from src.models.puzzle import Puzzle
from src.models.cage import Cage


def test_cage_index():
    grid = np.zeros((2, 2), dtype=int)

    cages = [
        Cage(3, [(0, 0), (0, 1)]),
        Cage(3, [(1, 0), (1, 1)])
    ]

    puzzle = Puzzle(grid, cages)

    assert puzzle.cage_index[0][0] == 0
    assert puzzle.cage_index[0][1] == 0
    assert puzzle.cage_index[1][0] == 1
    assert puzzle.cage_index[1][1] == 1