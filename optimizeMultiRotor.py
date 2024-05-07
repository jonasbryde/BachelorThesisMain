from minimumDistance import MinimumDistanceMultiRotor
from positionMultiRotor import positionMultiRotor
from sectorAEP import sectorAEP

def optimizeMultiRotor(f,A,k, wd, rows, collumns, boundaries, n_mr):
    minimumDistance = MinimumDistanceMultiRotor(f,A,k, wd, rows, collumns)
    position = positionMultiRotor(boundaries, minimumDistance, n_mr)
    AEP = sectorAEP(f,A,k,wd,ti,centers,my_wt)
    
    return position, AEP
