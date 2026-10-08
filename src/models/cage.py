class Cage:
    def __init__(self, target_sum, cells):
        self.target_sum = target_sum
        self.cells = cells

    def __repr__(self):
        return f"Cage(target_sum={self.target_sum}, cells={self.cells})"