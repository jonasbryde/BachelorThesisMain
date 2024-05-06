import numpy as np
from shapely.geometry import Polygon, Point
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as mpl_polygon
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from sectorAEP import sectorAEP



def positionMultiRotor(boundaries, minimumDistance, n_mr, f, A, k, wd, ti, turbineDiameter, turbineTipClearence, Columns, rows):

    #Defining the wind turbine object
    u = [0,3,12,25,30]
    ct = [0,8/9,8/9,.3, 0]
    power = [0,0,1000,1000,0]

    my_wt = WindTurbine(name='MyWT',
                        diameter=turbineDiameter,
                        hub_height=40,
                        powerCtFunction=PowerCtTabular(u,power,'kW',ct))

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

    aep = sectorAEP(f, A, k, wd, ti, positions, my_wt, turbineDiameter, turbineTipClearence, Columns, rows)

    return points, aep
