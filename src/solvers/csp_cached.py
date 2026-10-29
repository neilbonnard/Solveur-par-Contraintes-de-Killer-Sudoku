from itertools import combinations, permutations
from src.validator import Validator


class KillerSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.size = puzzle.grid.shape[0]
        self.blo_size = int(self.size ** 0.5)
        self.validator = Validator(puzzle)

        self.history = []
        self.domains = {}

        # Les cages de même taille et de même somme partagent les mêmes possibilités
        self.combinations_cache = {}
        self.assignments_cache = {}

        # Compteurs pour mesurer les performances
        self.nodes_explored = 0
        self.backtracks = 0
        self.propagations = 0

    def get_cage_combinations(self, cage):
        key = (len(cage.cells), cage.target_sum)

        if key not in self.combinations_cache:
            k, target_sum = key
            self.combinations_cache[key] = [
                combo
                for combo in combinations(range(1, self.size + 1), k)
                if sum(combo) == target_sum
            ]

        return self.combinations_cache[key]

    def get_cage_assignments(self, cage):
        key = (len(cage.cells), cage.target_sum)

        if key not in self.assignments_cache:
            # Chaque permutation correspond à une affectation possible des cases
            self.assignments_cache[key] = [
                perm
                for combo in self.get_cage_combinations(cage)
                for perm in permutations(combo)
            ]

        return self.assignments_cache[key]

    def initialize_domains(self):
        self.domains = {}

        for cage in self.puzzle.cages:
            combinations = self.get_cage_combinations(cage)

            possible_values = set()
            for combo in combinations:
                possible_values.update(combo)

            for row, col in cage.cells:
                value = self.puzzle.grid[row, col]

                if value == 0:
                    self.domains[(row, col)] = possible_values.copy()
                else:
                    self.domains[(row, col)] = {int(value)}

    def write_value(self, row, col, value, reason="guess"):
        if self.puzzle.grid[row, col] != 0:
            return False

        if value not in self.domains[(row, col)]:
            return False

        if not self.validator.is_valid_move(row, col, value):
            return False

        self.history.append(("grid", (row, col), 0))

        for val in self.domains[(row, col)].copy():
            if val != value:
                self.remove_from_domain(row, col, val)

        self.puzzle.grid[row, col] = value
        return True

    def remove_from_domain(self, row, col, value):
        if (row, col) not in self.domains:
            return False

        if value not in self.domains[(row, col)]:
            return False

        self.history.append(("domain", (row, col), value))
        self.domains[(row, col)].remove(value)
        return True

    def undo_to(self, checkpoint):
        if checkpoint < 0 or checkpoint > len(self.history):
            return False

        while len(self.history) > checkpoint:
            old_type, (row, col), old_value = self.history.pop()

            if old_type == "grid":
                self.puzzle.grid[row, col] = old_value

            elif old_type == "domain":
                self.domains[(row, col)].add(old_value)

        return True

    def get_neighbors(self, row, col):
        neighbors = set()

        # Cases de la même ligne et colonne
        for i in range(self.size):
            if i != col:
                neighbors.add((row, i))
            if i != row:
                neighbors.add((i, col))

        # Cases du même bloc
        start_row = (row // self.blo_size) * self.blo_size
        start_col = (col // self.blo_size) * self.blo_size

        for i in range(start_row, start_row + self.blo_size):
            for j in range(start_col, start_col + self.blo_size):
                if (i, j) != (row, col):
                    neighbors.add((i, j))

        # Cases de la même cage
        cage_id = self.puzzle.cage_index[row][col]
        cage = self.puzzle.cages[cage_id]

        for i, j in cage.cells:
            if (i, j) != (row, col):
                neighbors.add((i, j))

        return neighbors

    def propagate_cage(self, cage_id):
        cage = self.puzzle.cages[cage_id]
        cells = cage.cells

        # On récupère les domaines actuels des cases
        domains = [self.domains[(row, col)] for row, col in cells]

        # Les affectations possibles sont calculées une seule fois par type de cage
        assignments = self.get_cage_assignments(cage)
        possible_values = [set() for _ in cells]
        found = False

        for perm in assignments:
            if all(value in domain for value, domain in zip(perm, domains)):
                found = True
                for i, value in enumerate(perm):
                    possible_values[i].add(value)

        # Aucune affectation possible : contradiction
        if not found:
            return False

        # On retire les valeurs impossibles
        for i, (row, col) in enumerate(cells):
            for value in self.domains[(row, col)].copy():
                if value not in possible_values[i]:
                    self.remove_from_domain(row, col, value)

        return True

    def propagate(self):
        # Un appel à propagate = une propagation
        self.propagations += 1

        changed = True

        while changed:
            changed = False
            checkpoint = len(self.history)

            # Propagation AllDifferent
            for (row, col), domain in self.domains.items():

                if len(domain) == 0:
                    return False

                if len(domain) == 1:
                    value = next(iter(domain))

                    if self.puzzle.grid[row, col] == 0:
                        if not self.write_value(row, col, value, reason="deduction"):
                            return False

                    for i, j in self.get_neighbors(row, col):
                        if value in self.domains[(i, j)]:
                            self.remove_from_domain(i, j, value)

                            if len(self.domains[(i, j)]) == 0:
                                return False

            # Propagation des sommes des cages
            for cage_id in range(len(self.puzzle.cages)):
                if not self.propagate_cage(cage_id):
                    return False

            if len(self.history) > checkpoint:
                changed = True

        return True

    def select_variable(self):
        # MRV : choisir la case avec le plus petit domaine > 1
        min_domain_size = float("inf")
        selected_var = None

        for (row, col), domain in self.domains.items():
            if 1 < len(domain) < min_domain_size:
                min_domain_size = len(domain)
                selected_var = (row, col)

        return selected_var

    def search(self):
        selected_var = self.select_variable()

        if selected_var is None:
            return bool(self.validator.is_solved())

        row, col = selected_var

        for value in sorted(self.domains[(row, col)]):
            # Une nouvelle hypothèse est testée
            self.nodes_explored += 1

            checkpoint = len(self.history)

            if self.write_value(row, col, value):
                if self.propagate():
                    if self.search():
                        return True

            # Cette hypothèse n'a pas abouti
            self.backtracks += 1
            self.undo_to(checkpoint)

        return False

    def solve(self):
        # Réinitialisation des compteurs pour chaque résolution
        self.nodes_explored = 0
        self.backtracks = 0
        self.propagations = 0
        self.history = []

        self.initialize_domains()

        if not self.propagate():
            return False

        return self.search()