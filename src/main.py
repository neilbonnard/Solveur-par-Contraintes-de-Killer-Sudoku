import csv
import time
from pathlib import Path

from src.puzzle_loader import load_json
from src.solvers.csp import KillerSolver


def main():
    puzzles_dir = Path("data/dataset-puzzles")
    results_dir = Path("benchmarks")
    results_dir.mkdir(exist_ok=True)

    results = []

    # On récupère tous les puzzles JSON
    puzzle_files = sorted(puzzles_dir.glob("*.json"))

    for filepath in puzzle_files:
        print(f"Résolution de {filepath.name}...")

        puzzle = load_json(filepath)
        solver = KillerSolver(puzzle)

        start = time.perf_counter()
        solved = solver.solve()
        elapsed = time.perf_counter() - start

        # On vérifie la solution trouvée
        valid = bool(solved and solver.validator.is_solved())

        results.append({
            "puzzle": filepath.name,
            "solved": solved,
            "valid": valid,
            "time_seconds": round(elapsed, 4),
            "nodes_explored": solver.nodes_explored,
            "backtracks": solver.backtracks,
            "propagations": solver.propagations
        })

        print(f"  Résolu : {solved}")
        print(f"  Valide : {valid}")
        print(f"  Temps : {elapsed:.4f} s\n")

    # Sauvegarde des résultats
    output = results_dir / "results.csv"

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "puzzle",
            "solved",
            "valid",
            "time_seconds",
            "nodes_explored",
            "backtracks",
            "propagations"
        ])

        writer.writeheader()
        writer.writerows(results)

    print(f"\nRésultats enregistrés dans {output}")


if __name__ == "__main__":
    main()