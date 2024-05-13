import numpy as np
from topfarm.cost_models.py_wake_wrapper import PyWakeAEPCostModelComponent   
from topfarm import TopFarmProblem
from topfarm.easy_drivers import EasyScipyOptimizeDriver
from topfarm.plotting import NoPlot, XYPlotComp
from py_wake import NOJ
from py_wake.site import XRSite
import xarray as xr
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
import numpy as np
from topfarm.constraint_components.boundary import XYBoundaryConstraint
from topfarm.constraint_components.spacing import SpacingConstraint
from initializeTurbines import initializeTurbines


aep_values=[]
sorted_aep_values = []

def optimizeSingleTurbines(boundaries, n_wt, min_initial_distance, f, A, k):

    initial = initializeTurbines(boundaries, n_wt, 1500)

    boundaryConstraint = XYBoundaryConstraint(boundaries, 'polygon')

    spacingConstraint = SpacingConstraint(240*5)
    
    wd = np.linspace(0, 360, len(f), endpoint=False)
    ti = 0.1

    site = XRSite(ds = xr.Dataset(data_vars={'Sector_frequency': ('wd', f), 'Weibull_A': ('wd', A), 'Weibull_k': ('wd', k), 'TI': ti},
                                coords={'wd': wd}))

    #Defining the wind turbine object
    u = [0,3,5,7,9,10.59,15,20,25,26]
    power = [0,0,2000,5000,10000,15000,15000,15000,15000,0]
    ct = [0,0.8,0.8,0.8,0.8,0.8,0.3,0.1,0.1,0]
    

    wind_turbines = WindTurbine(name='MyWT',
                        diameter=240,
                        hub_height=150,
                        powerCtFunction=PowerCtTabular(u,power,'kW',ct))

    wfmodel = NOJ(site, wind_turbines)   

    cost_comp = PyWakeAEPCostModelComponent(wfmodel, n_wt, wd=wd)

    driver = EasyScipyOptimizeDriver(maxiter=420)

    design_vars = dict(zip('xy', (initial[:, :2]).T))

    tf_problem = TopFarmProblem(
                design_vars,
                cost_comp,
                constraints = [boundaryConstraint, spacingConstraint],
                driver=driver,
                plot_comp=XYPlotComp())

    cost, state, recorder = tf_problem.optimize()
    
    aep_values.append(recorder['AEP'])



    return design_vars, state, aep_values
