from src.models.puzzle import Puzzle
from src.validator import Validator
from src.models.cage import Cage


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
            old_domain = self.domains[(row, col)].copy()
            self.history.append(((row, col), 0, old_domain))

            # On affecte la valeur et on réduit son domaine
            self.puzzle.grid[row, col] = value
            self.domains[(row, col)] = {value}

            return True

        return False

    def erase_value(self, row, col):
        if not self.history:
            return False

        # On vérifie que c'est bien la dernière case modifiée
        last_position = self.history[-1][0]

        if last_position != (row, col):
            return False

        return self.undo()

    def initialize_domains(self):
        # On initialise le domaine de chaque case de la grille
        for row in range(self.size):
            for col in range(self.size):
                value = self.puzzle.grid[row, col]

                if value == 0:
                    # Case vide : toutes les valeurs sont possibles au départ
                    self.domains[(row, col)] = set(range(1, self.size + 1))
                else:
                    # Case déjà remplie : une seule valeur possible
                    self.domains[(row, col)] = {int(value)}

    def undo(self):
        if not self.history:
            return False

        # On récupère la dernière modification
        (row, col), old_value, old_domain = self.history.pop()

        # On restaure la case et son domaine
        self.puzzle.grid[row, col] = old_value
        self.domains[(row, col)] = old_domain

        return True
