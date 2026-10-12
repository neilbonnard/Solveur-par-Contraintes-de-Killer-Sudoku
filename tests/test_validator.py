import numpy as np
from src.models.puzzle import Puzzle
from src.models.cage import Cage
from src.validator import Validator


def create_validator():
    grid = np.array([
        [1, 2, 3, 4],
        [3, 4, 1, 2],
        [2, 1, 4, 3],
        [4, 3, 2, 1]
    ])

    cages = [
        Cage(3, [(0, 0), (0, 1)]),
        Cage(7, [(0, 2), (0, 3)]),
        Cage(7, [(1, 0), (1, 1)]),
        Cage(3, [(1, 2), (1, 3)]),
        Cage(3, [(2, 0), (2, 1)]),
        Cage(7, [(2, 2), (2, 3)]),
        Cage(7, [(3, 0), (3, 1)]),
        Cage(3, [(3, 2), (3, 3)])
    ]

    return Validator(Puzzle(grid, cages))


def test_valid_solution():
    validator = create_validator()
    assert validator.is_solved() is True


def test_invalid_row():
    validator = create_validator()
    validator.puzzle.grid[0, 1] = 1
    assert validator.check_row(0) is False


def test_invalid_column():
    validator = create_validator()
    validator.puzzle.grid[1, 0] = 1
    assert validator.check_column(0) is False


def test_invalid_block():
    validator = create_validator()
    validator.puzzle.grid[1, 1] = 1
    assert validator.check_block(0, 0, 2) is False


def test_invalid_cage_sum():
    validator = create_validator()
    validator.puzzle.grid[0, 0] = 4
    assert validator.check_cage(0) is False


def test_valid_move_restores_grid():
    validator = create_validator()
    validator.puzzle.grid[0, 0] = 0

    assert validator.is_valid_move(0, 0, 1) is True
    assert validator.puzzle.grid[0, 0] == 0


def test_invalid_move_restores_grid():
    validator = create_validator()
    validator.puzzle.grid[0, 0] = 0

    assert validator.is_valid_move(0, 0, 2) is False
    assert validator.puzzle.grid[0, 0] == 0


def test_incomplete_grid_not_solved():
    validator = create_validator()
    validator.puzzle.grid[0, 0] = 0

    assert validator.is_solved() is False