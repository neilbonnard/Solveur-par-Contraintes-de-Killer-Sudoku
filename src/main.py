from puzzle_loader import load_json, load_txt

puzzle = load_txt("data/4x4-puzzles/easy-killer-44-01.in")

print(puzzle.grid)
print(puzzle.cage_index)