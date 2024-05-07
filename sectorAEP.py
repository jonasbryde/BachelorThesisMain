from py_wake import NOJ
import xarray as xr
from py_wake.site import XRSite
import generateMultiRotorCoordinates


def sectorAEP(f, A, k, wd, ti, centers, my_wt, turbineDiameter, turbineTipClearence, Columns, rows):

    #list of AEPs for each sector
    AEP_list = []

    # Loop through each position of A and k
    for i in range(len(A)):
        # Create new lists with zeros
        new_f = [0] * len(f)

        #only the current position to its value
        new_f[i] = 1

        #Define the site object
        site = XRSite(
            ds=xr.Dataset(data_vars={'Sector_frequency': ('wd', new_f), 'Weibull_A': ('wd', A), 'Weibull_k': ('wd', k), 'TI': ti},
                            coords={'wd': wd}))


        #Receiving coordinates from the function GenerateMultiRotorCoordinates in the file GenerateMultiRotorCoordinates.py
        coordinates = generateMultiRotorCoordinates.generateMultiRotorCoordinates(centers, i, turbineDiameter, turbineTipClearence, Columns, rows)

        x_cord = coordinates["xCoordinates"]
        y_cord = coordinates["yCoordinates"]
        z_cord = coordinates["zCoordinates"]

        #creating the wind farm model
        noj = NOJ(site, my_wt)

        # Simulating results from the wind farm model and turbine coordinates
        simulationResult = noj(x_cord, y_cord, z_cord)

        # Calculating AEP
        aep = simulationResult.aep()

        # new list with new AEPs
        AEP_list.append((round(aep.sum().item(), 2)))

    total_aep = sum(AEP_list)

    avg_aep = round(total_aep / len(AEP_list), 2)

    return(avg_aep)
