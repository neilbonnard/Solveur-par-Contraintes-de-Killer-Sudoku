import json
from pathlib import Path
from collections import defaultdict

from src.puzzle_loader import load_json
from src.validator import Validator


source = Path("data/raw/KillerSudoku_dataset_000.json")
folder = Path("data/dataset-puzzles")

with open(source, encoding="utf-8") as f:
    dataset = json.load(f)

# On reprend les 20 premiers puzzles 9x9,
# dans le même ordre que notre convertisseur
originals = []

for puzzle_id, puzzle in dataset["data"].items():
    size = int(puzzle["problem"].splitlines()[0].split()[0])
    if size == 9:
        originals.append((puzzle_id, puzzle))
    if len(originals) == 20:
        break


def check_puzzle(filepath, original):
    puzzle = load_json(filepath)
    lines = original["problem"].splitlines()

    # Sommes et identifiants de cages du fichier original
    sums = [line.split() for line in lines[1:10]]
    cage_ids = [
        list(map(int, line.split()))
        for line in lines[10:19]
    ]

    original_cages = defaultdict(list)
    original_sums = defaultdict(list)

    for row in range(9):
        for col in range(9):
            cage_id = cage_ids[row][col]
            original_cages[cage_id].append((row, col))

            if sums[row][col] != "-":
                original_sums[cage_id].append(int(sums[row][col]))

    # Reconstruction indépendante des cages attendues
    expected = set()

    for cage_id, cells in original_cages.items():
        assert len(original_sums[cage_id]) == 1
        expected.add((
            original_sums[cage_id][0],
            frozenset(cells)
        ))

    # Cages présentes dans notre fichier converti
    actual = {
        (cage.target_sum, frozenset(cage.cells))
        for cage in puzzle.cages
    }

    assert actual == expected, "Les cages ne correspondent pas"
    assert len(puzzle.cages) == len(expected)

    # Chaque case doit appartenir à une seule cage
    all_cells = [
        cell
        for cage in puzzle.cages
        for cell in cage.cells
    ]

    assert len(all_cells) == 81
    assert len(set(all_cells)) == 81
    assert set(all_cells) == {
        (r, c) for r in range(9) for c in range(9)
    }

    # Vérification des sommes avec la solution officielle
    solution_lines = original["solution"].splitlines()
    assert solution_lines[0].split() == ["9", "9"]

    solution = [
        list(map(int, line.split()))
        for line in solution_lines[1:10]
    ]

    for cage in puzzle.cages:
        values = [solution[r][c] for r, c in cage.cells]
        assert sum(values) == cage.target_sum
        assert len(values) == len(set(values))

    # Le validateur doit également accepter la solution
    puzzle.grid[:, :] = solution
    assert Validator(puzzle).is_solved()

    return solution


for i, (puzzle_id, original) in enumerate(originals, start=1):
    filepath = folder / f"puzzle_{i:03d}.json"

    try:
        check_puzzle(filepath, original)
        print(f"{filepath.name} : OK (source : {puzzle_id})")
    except Exception as e:
        print(f"{filepath.name} : ERREUR - {e}")
        raise

print("\nVérification terminée : 20 puzzles contrôlés.")