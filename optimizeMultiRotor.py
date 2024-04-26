from MinimumDistanceMultiRotor import MinimumDistanceMultiRotor
from positionMultiRotor import positionMultiRotor

def optimizeMultiRotor(f,A,k, wd, rows, collumns, boundaries, n_mr):
    minimumDistance = MinimumDistanceMultiRotor(f,A,k, wd, rows, collumns)
    position = positionMultiRotor(boundaries, minimumDistance, n_mr)
    
    return position
