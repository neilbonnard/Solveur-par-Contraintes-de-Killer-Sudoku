import numpy as np

class Validator:
    def __init__(self, puzzle):
        self.puzzle = puzzle

    def check_row(self, row):
        row = self.puzzle.grid[row]
        row = row[row != 0]
        set1 = set(row)
        return len(set1) == len(row)

    def check_column(self, column):
        col = []
        for i in range(self.puzzle.grid.shape[0]):
            col.append(self.puzzle.grid[i][column])
        col = [value for value in col if value != 0]
        return len(set(col)) == len(col)

    def check_block(self, row, col, blo_size):
        startrow = row // blo_size * blo_size
        startcol = col // blo_size * blo_size
        blo = []
        for i in range(blo_size):
            for n in range(blo_size):
                blo.append(self.puzzle.grid[startrow+i][n+startcol])

        blo = [value for value in blo if value != 0]
        return len(set(blo)) == len(blo)

    def check_cage(self, cage_id):
        cage = self.puzzle.cages[cage_id]
        total = 0
        values = []

        for x, y in cage.cells:
            value = self.puzzle.grid[x][y]
            total += value
            if value != 0:
                values.append(value)

        if len(values) != len(set(values)):
            return False

        if total > cage.target_sum:
            return False

        if len(values) == len(cage.cells):
            return total == cage.target_sum

        return True

    def is_valid_move(self, row, col, value):
        init_val = self.puzzle.grid[row, col]
        self.puzzle.grid[row, col] = value
        cage_id = self.puzzle.cage_index[row][col]
        blo_size = int(self.puzzle.grid.shape[0] ** 0.5)

        valid = (
            self.check_row(row)
            and self.check_column(col)
            and self.check_block(row, col, blo_size)
            and self.check_cage(cage_id)
        )

        self.puzzle.grid[row, col] = init_val
        return bool(valid)

    def is_solved(self):
        grid = self.puzzle.grid
        n = grid.shape[0]
        blo_size = int(n ** 0.5)

        # Toutes les cases doivent contenir une valeur entre 1 et n
        if not np.all((grid >= 1) & (grid <= n)):
            return False

        # Vérification des lignes et colonnes
        for i in range(n):
            if not self.check_row(i) or not self.check_column(i):
                return False

        # Vérification des blocs
        for row in range(0, n, blo_size):
            for col in range(0, n, blo_size):
                if not self.check_block(row, col, blo_size):
                    return False

        # Vérification des cages
        for cage_id in range(len(self.puzzle.cages)):
            if not self.check_cage(cage_id):
                return False

        return True

