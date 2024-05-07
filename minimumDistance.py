from py_wake.site import XRSite
import xarray as xr
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from generateMultiRotorCoordinates import generateMultiRotorCoordinates
from py_wake import NOJ
import numpy as np

def MinimumDistanceMultiRotor(f,A,k,wd,rows,collumns,turbineDiameter,turbineTipClearence):
    #find the index with the max speed
    maxspeed_index = 0 

    for i in range(len(A)):
        if A[i] > A[maxspeed_index]:
            maxspeed_index = i 

    newF = [1,0]
    newA = [A[maxspeed_index], A[maxspeed_index]]
    newK = [k[maxspeed_index], k[maxspeed_index]]
    ti = 0.1
    newWd = np.linspace(0, 360, len(newF), endpoint=False)

    site = XRSite(ds = xr.Dataset(data_vars={'Sector_frequency': ('wd', newF), 'Weibull_A': ('wd', newA), 'Weibull_k': ('wd', newK), 'TI': ti},
                            coords={'wd': newWd}))
    
    #define turbine stats for multiRotor
    u = [0,4,6.5,7.5,9,10,13.5,15,20,25,26]
    ct = [1,1,0.8,0.7,0.6,0.6,0.5,0.4,0.3,0.25,0]
    power = [0,0,200,400,600,800,1000,1000,1000,1000,0]

    my_wt = WindTurbine(name='MyWT',
                    diameter=turbineDiameter,
                    hub_height=40,
                    powerCtFunction=PowerCtTabular(u,power,'kW',ct))
    
    #Find AEP at very large distance where wake is insignificant

    AEPGoal = 0 
    centers = [[0,0,0], [0,20000,0]]
    coordinates = generateMultiRotorCoordinates(centers,0,turbineDiameter,turbineTipClearence,collumns,rows)
    x_cord = coordinates["xCoordinates"]
    y_cord = coordinates["yCoordinates"]
    z_cord = coordinates["zCoordinates"]

    noj = NOJ(site, my_wt)
    
    simulationResult = noj(x_cord, y_cord, z_cord)

    AEPGoal = round(simulationResult.aep().sum().item(), 2)

    #loop through distances to find distance where wake has no effect
    minimumDistance = 0 
    conditions = False
    testAEPs = list()

    while conditions == False:

        minimumDistance += 100
        centers = [[0,0,0],[0,minimumDistance,0]]
        coordinates = generateMultiRotorCoordinates(centers,0,turbineDiameter,turbineTipClearence,collumns,rows)
        x_cord = coordinates["xCoordinates"]
        y_cord = coordinates["yCoordinates"]
        z_cord = coordinates["zCoordinates"]

        simulationResult = noj(x_cord, y_cord, z_cord)

        testAEPs.append(round(simulationResult.aep().sum().item(), 0))
        print("testAEP is currently:", str(testAEPs[len(testAEPs) - 1 ]), " at the distance: ", str(minimumDistance))
        print("")

        if len(testAEPs) > 2:
            if testAEPs[len(testAEPs) - 1] > 0.99 * AEPGoal or testAEPs[len(testAEPs) - 1] == testAEPs[len(testAEPs) - 2]:
                conditions = True



    return minimumDistance
