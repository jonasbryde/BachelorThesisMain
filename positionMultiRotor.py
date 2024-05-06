import numpy as np
from shapely.geometry import Polygon, Point
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mpl_polygon

def positionMultiRotor(boundaries, minimumDistance, n_mr):
    outerBoundary = Polygon(boundaries)
    min_x, min_y, max_x, max_y = outerBoundary.bounds

    positions = [[boundaries[0][0], boundaries[0][1]]]

    for i in range(n_mr - 1):

        PointApproved = False
        while PointApproved == False:
            point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            for i in range(len(positions)):
                if outerBoundary.contains(point) and np.sqrt((positions[i][1] - point.y)**2 + (positions[i][0]-point.x)**2) >= minimumDistance:
                    PointApproved = True
                else:
                    PointApproved = False
                    break   
        
        positions.append([point.x, point.y])

    points = {"x": np.array([point[0] for point in positions]), "y": np.array([point[1] for point in positions])}
    return points
