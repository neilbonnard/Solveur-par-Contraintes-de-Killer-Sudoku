import numpy as np
from src.models.puzzle import Puzzle
from src.models.cage import Cage
from src.solvers.csp import KillerSolver


def create_solver():
    grid = np.zeros((4, 4), dtype=int)

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

    solver = KillerSolver(Puzzle(grid, cages))
    solver.initialize_domains()
    return solver


def test_cage_combinations():
    solver = create_solver()
    cage = solver.puzzle.cages[0]

    assert solver.get_cage_combinations(cage) == [(1, 2)]


def test_initialize_domains():
    solver = create_solver()

    assert solver.domains[(0, 0)] == {1, 2}
    assert solver.domains[(0, 2)] == {3, 4}


def test_get_neighbors():
    solver = create_solver()

    neighbors = solver.get_neighbors(0, 0)

    assert (0, 1) in neighbors
    assert (1, 0) in neighbors
    assert (1, 1) in neighbors
    assert (3, 3) not in neighbors
    assert (0, 0) not in neighbors


def test_write_value():
    solver = create_solver()

    assert solver.write_value(0, 0, 1) is True
    assert solver.puzzle.grid[0, 0] == 1
    assert solver.domains[(0, 0)] == {1}


def test_invalid_write():
    solver = create_solver()

    assert solver.write_value(0, 0, 4) is False
    assert solver.puzzle.grid[0, 0] == 0


def test_remove_from_domain():
    solver = create_solver()

    assert solver.remove_from_domain(0, 0, 1) is True
    assert solver.domains[(0, 0)] == {2}


def test_undo_to():
    solver = create_solver()

    checkpoint = len(solver.history)

    solver.write_value(0, 0, 1)
    solver.remove_from_domain(0, 2, 3)

    assert solver.undo_to(checkpoint) is True

    assert solver.puzzle.grid[0, 0] == 0
    assert solver.domains[(0, 0)] == {1, 2}
    assert solver.domains[(0, 2)] == {3, 4}
    assert len(solver.history) == checkpoint