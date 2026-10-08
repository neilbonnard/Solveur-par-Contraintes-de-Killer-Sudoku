class Validator:
    def __init__(self, puzzle):
        self.puzzle = puzzle

    def check_row(self, row):
        row = self.puzzle.grid[row]
        row = row[row != 0]
        set1 = set(row)
        return len(set1) == len(row)
    
    def check_column(self, column):
        col=[]
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
                blo.append(self.puzzle.grid[startrow+i][n +startcol])

        blo = [value for value in blo if value != 0]
        return len(set(blo)) == len(blo)

    def check_cage(self, cages):
        pass

    def is_valid_move(self, row, col, value):
        pass

    def is_solved(self):
        pass

