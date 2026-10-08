import numpy as np

class Puzzle:
    def __init__(self, grid, cages):
        self.grid = grid
        self.cages = cages
        self.cage_index = self.build_cage_index()

    def build_cage_index(self):
        cindex=[]
        for x in range(self.grid.shape[0]):
            ar = []
        
            for y in range(self.grid.shape[0]):
                for cage in range(len(self.cages)):
                    if (x,y) in self.cages[cage].cells:
                        ar.append(cage)
                        break
            cindex.append(ar)
        return cindex
    
    
