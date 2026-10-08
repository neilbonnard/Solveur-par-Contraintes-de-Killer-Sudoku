import json
import numpy as np

from models.puzzle import Puzzle
from models.cage import Cage


def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    grid = np.array(data["board"], dtype=int)

    cages = [
        Cage(target_sum, [tuple(cell) for cell in cells])
        for target_sum, cells in data["cages"]
    ]

    return Puzzle(grid, cages)


def load_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    size = int(lines[0])
    nb_cages = int(lines[2])

    grid = np.zeros((size, size), dtype=int)
    cages = []

    for line in lines[3:3 + nb_cages]:
        parts = line.split()

        target_sum = int(parts[0])
        cells = [tuple(map(int, cell.split(","))) for cell in parts[1:]]

        cages.append(Cage(target_sum, cells))

    return Puzzle(grid, cages)