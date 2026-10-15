from src.models.puzzle import Puzzle
from src.validator import Validator
from src.models.cage import Cage
from itertools import combinations


class KillerSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.size = puzzle.grid.shape[0]
        self.blo_size = int(self.size ** 0.5)
        self.validator = Validator(puzzle)
        self.history = []  # Liste pour stocker l'historique des mouvements effectués
        # Dictionnaire qui contiendra les valeurs possibles de chaque case
        self.domains = {}

    def write_value(self, row, col, value):
        if self.puzzle.grid[row, col] != 0:
            return False

        if value not in self.domains[(row, col)]:
            return False

        if self.validator.is_valid_move(row, col, value):
            # On sauvegarde l'état avant la modification
            init_val = self.puzzle.grid[row, col]
            old_domain = self.domains[(row, col)].copy()
            self.history.append(("grid", (row, col), int(init_val)))
            for val in old_domain:
                if val != value:
                    self.history.append(("domain", (row, col), val))

            # On affecte la valeur et on réduit son domaine
            self.puzzle.grid[row, col] = value
            self.domains[(row, col)] = {value}

            return True

        return False

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

    def undo_to(self, checkpoint):
        if len(self.history) < checkpoint or checkpoint < 0:
            return False

        while len(self.history) > checkpoint:
            
            old_type, (row, col), old_value = self.history.pop()

            # On restaure la case et son domaine
            if old_type == "grid":
                self.puzzle.grid[row, col] = old_value

            elif old_type == "domain":
                self.domains[(row, col)].add(old_value)

        return True

    def remove_from_domain(self, row, col, value):
        if (row, col) not in self.domains:
            return False

        if value not in self.domains[(row, col)]:
            return False

        # On sauvegarde l'état avant la modification
        self.history.append(("domain", (row, col), value))
        self.domains[(row, col)].remove(value)
        return True



    def get_neighbors(self, row, col):
        neighbors = set()

        # On ajoute les cases de la même ligne et de la même colonne
        for i in range(self.size):
            if i != col:
                neighbors.add((row, i))
            if i != row:
                neighbors.add((i, col))

        # On ajoute les cases du même bloc
        start_row = (row // self.blo_size) * self.blo_size
        start_col = (col // self.blo_size) * self.blo_size

        for i in range(start_row, start_row + self.blo_size):
            for j in range(start_col, start_col + self.blo_size):
                if (i, j) != (row, col):
                    neighbors.add((i, j))

        # On ajoute les cases de la meme cage
        cage_id = self.puzzle.cage_index[row][col]
        cage = self.puzzle.cages[cage_id]

        for i, j in cage.cells:
            if (i, j) != (row, col):
                neighbors.add((i, j))

        return neighbors

    def get_cage_combinations(self, cage):
        numbers = range(1, self.size + 1)
        k = len(cage.cells)

        return [
            combo
            for combo in combinations(numbers, k)
            if sum(combo) == cage.target_sum
        ]
    
    def propagate(self):
        changed = True

        # On continue tant que les domaines évoluent
        while changed:
            changed = False

            for (row, col), domain in self.domains.items():

                # Si une case n'a plus de valeur possible : contradiction
                if len(domain) == 0:
                    return False

                # Si une seule valeur est possible
                if len(domain) == 1:
                    value = next(iter(domain))

                    # On retire cette valeur des domaines des voisins
                    for i, j in self.get_neighbors(row, col):
                        if value in self.domains[(i, j)]:
                            self.remove_from_domain(i, j, value)
                            changed = True

                            # Un domaine vide signifie une contradiction
                            if len(self.domains[(i, j)]) == 0:
                                return False

        return True