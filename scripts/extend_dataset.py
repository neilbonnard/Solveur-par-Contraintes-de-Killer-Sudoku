import json
import random
from pathlib import Path
from collections import defaultdict

raw_dir = Path("data/raw")
output_dir = Path("data/dataset-puzzles")
output_dir.mkdir(parents=True, exist_ok=True)

rng = random.Random(42)  # Même sélection à chaque exécution

# Chargement des deux fichiers
puzzles = {}

for filepath in sorted(raw_dir.glob("KillerSudoku_dataset_*.json")):
    with open(filepath, encoding="utf-8") as f:
        dataset = json.load(f)

    puzzles.update(dataset["data"])


def convert_puzzle(puzzle):
    lines = puzzle["problem"].splitlines()
    size = int(lines[0].split()[0])

    sums = [line.split() for line in lines[1:1 + size]]
    cage_ids = [
        list(map(int, line.split()))
        for line in lines[1 + size:1 + 2 * size]
    ]

    cells_by_cage = defaultdict(list)
    sums_by_cage = defaultdict(list)

    for row in range(size):
        for col in range(size):
            cage_id = cage_ids[row][col]
            cells_by_cage[cage_id].append([row, col])

            if sums[row][col] != "-":
                sums_by_cage[cage_id].append(int(sums[row][col]))

    cages = []

    for cage_id, cells in cells_by_cage.items():
        targets = sums_by_cage[cage_id]

        if len(targets) != 1:
            raise ValueError(f"Cage invalide : {cage_id}")

        cages.append([targets[0], cells])

    return {
        "board": [[0] * size for _ in range(size)],
        "cages": cages
    }


# Seulement les puzzles 9x9
candidates = [
    (puzzle_id, puzzle)
    for puzzle_id, puzzle in puzzles.items()
    if puzzle["problem"].startswith("9 9\n")
]

# Les 20 premiers ont déjà été convertis
existing_ids = {pid for pid, _ in candidates[:20]}
remaining = [
    (pid, puzzle)
    for pid, puzzle in candidates
    if pid not in existing_ids
]

# Trier selon le nombre de cages
remaining.sort(
    key=lambda item: len(convert_puzzle(item[1])["cages"])
)

# Diviser en 4 groupes avec des nombres de cages différents
groups = [
    remaining[i * len(remaining) // 4:
              (i + 1) * len(remaining) // 4]
    for i in range(4)
]

# Sélectionner 20 puzzles dans chaque groupe
selected = []

for group in groups:
    selected.extend(rng.sample(group, 20))

rng.shuffle(selected)

# Ajouter les nouveaux puzzles sans remplacer les anciens
for index, (puzzle_id, puzzle) in enumerate(selected, start=21):
    converted = convert_puzzle(puzzle)

    output = output_dir / f"puzzle_{index:03d}.json"

    with open(output, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2)

print(f"{len(selected)} nouveaux puzzles ajoutés")
print(f"Total attendu : 100 puzzles 9x9")