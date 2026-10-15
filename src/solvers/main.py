from puzzle_loader import load_json, load_txt
from validator import Validator


puzzle = load_txt("data/4x4-puzzles/easy-killer-44-01.in")
validator = Validator(puzzle)

print(puzzle.grid)
print(puzzle.cage_index)

print(validator.is_valid_move(0, 0, 2))