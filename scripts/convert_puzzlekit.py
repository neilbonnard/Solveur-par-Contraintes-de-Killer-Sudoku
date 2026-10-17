import json
from pathlib import Path
from collections import defaultdict

source = Path("data/raw/KillerSudoku_dataset_000.json")
destination = Path("data/dataset-puzzles")
destination.mkdir(parents=True, exist_ok=True)

with open(source, "r", encoding="utf-8") as f:
    dataset = json.load(f)

count = 0

for puzzle_id, puzzle in dataset["data"].items():
    if count >= 20:
        break

    lines = puzzle["problem"].splitlines()
    size = int(lines[0].split()[0])

    # On ne garde que les grilles 9x9
    if size != 9:
        continue

    # Première matrice : sommes des cages
    sums = [line.split() for line in lines[1:10]]

    # Deuxième matrice : identifiants des cages
    cage_ids = [
        list(map(int, line.split()))
        for line in lines[10:19]
    ]

    cells_by_cage = defaultdict(list)
    sums_by_cage = defaultdict(list)

    for row in range(9):
        for col in range(9):
            cage_id = cage_ids[row][col]
            cells_by_cage[cage_id].append([row, col])

            if sums[row][col] != "-":
                sums_by_cage[cage_id].append(int(sums[row][col]))

    cages = []

    for cage_id, cells in cells_by_cage.items():
        # Chaque cage doit avoir exactement une somme cible
        if len(sums_by_cage[cage_id]) != 1:
            raise ValueError(f"Cage {cage_id} invalide dans {puzzle_id}")

        cages.append([sums_by_cage[cage_id][0], cells])

    converted = {
        "board": [[0] * 9 for _ in range(9)],
        "cages": cages
    }

    output = destination / f"puzzle_{count + 1:03d}.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2)

    count += 1

print(f"{count} puzzles convertis !")