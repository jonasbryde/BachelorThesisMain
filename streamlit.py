import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from scipy.stats import weibull_min
from initializeTurbines import initializeTurbines
from topfarm.constraint_components.boundary import XYBoundaryConstraint
from py_wake import NOJ
from py_wake.site import XRSite
import xarray as xr
from py_wake.wind_turbines import WindTurbine
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from topfarm.cost_models.py_wake_wrapper import PyWakeAEPCostModelComponent
from topfarm import TopFarmProblem
from topfarm.easy_drivers import EasyScipyOptimizeDriver
from topfarm.plotting import NoPlot, XYPlotComp
from minimumDistance import MinimumDistanceMultiRotor
from optimizeSingleTurbines import optimizeSingleTurbines
from positionMultiRotor import positionMultiRotor
from PerformWindAnalysis import perform_wind_analysis
from pyproj import Proj, transform
import ast
import time
from plotAEP import plotAEP
from plotMAP import plotMAP

def main():

    st.title("Wind analysis and wind turbine optimization")

    start_date_formatted = 20180101
    end_date_formatted = 20230101

    if 'f' not in st.session_state:
        st.session_state['f'] = list

    if 'A' not in st.session_state:
        st.session_state['A'] = list

    if 'k' not in st.session_state:
        st.session_state['k'] = list

    if 'initial' not in st.session_state:
        st.session_state['initial'] = list

    if 'state' not in st.session_state:
        st.session_state['state'] = list

    if 'wd' not in st.session_state:
        st.session_state['wd'] = list
    
    if 'rows' not in st.session_state:
        st.session_state['rows'] = int

    if 'columns' not in st.session_state:
        st.session_state['columns'] = int

    if 'n_mrs' not in st.session_state:
        st.session_state['n_mrs'] = int

    option = st.selectbox(
    "What area do you want to analyze?",
    ("Utsira Nord", "Sørlige Nordsjø II"),index=None, placeholder="Select area...",)
    st.write('You selected:', option)

    rotorType = st.selectbox(
        "Choose wind turbine type",
        ("Single Rotor", "Multi Rotor"), index=None, placeholder="Select turbine type..."
    )
    st.write('You selected:', rotorType)

    












    if option == 'Sørlige Nordsjø II' and rotorType == 'Single Rotor':
        latitude, longitude = 56.8233333, 4.3466667
        boundaries = [(6290955.204, 652660.403),(6282111.501,638361.822),(6305186.834, 624490.471),(6308047.231,622444.994),(6307693.262,620983.393),(6309020.039,620539.306),(6311673.489,621616.735),(6312254.677,639948.895),(6311985.300,641080.079)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        n_wt = 100
        st.write('The capasity at',option,'is',str(n_wt),'turbines')

        if st.button("Optimize Wind Farm"):
            with st.spinner('Wait for it...'):
                st.session_state['initial'], st.session_state['state'], aep_values = optimizeSingleTurbines(boundaries, n_wt, 1000, st.session_state['f'], st.session_state['A'], st.session_state['k'])
                y_coords = st.session_state['state']['x']
                x_coords = st.session_state['state']['y']
                plotMAP(x_coords,y_coords)
                plotAEP(aep_values)
                


    elif option == 'Sørlige Nordsjø II' and rotorType == 'Multi Rotor':
        latitude, longitude = 56.8233333, 4.3466667
        boundaries = [(6290955.204, 652660.403),(6282111.501,638361.822),(6305186.834, 624490.471),(6308047.231,622444.994),(6307693.262,620983.393),(6309020.039,620539.306),(6311673.489,621616.735),(6312254.677,639948.895),(6311985.300,641080.079)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        st.session_state['wd'] = np.linspace(0, 360, len(st.session_state['f']), endpoint=False)

        ti = 0.1

        st.session_state['rows'] = st.selectbox(
            "Choose how many rows the multi rotor systems will include",
            (2,3,4,5,6,7,8), index=None, placeholder="Select number rows..."
        )
        st.write('You selected:', str(st.session_state['rows']), "number of rows")
        st.session_state['columns'] = st.selectbox(
            "Choose how many columns the multi rotor systems will include",
            (2,3,4,5,6,7,8), index=None, placeholder="Select number columns..."
        )
        st.write('You selected:', str(st.session_state['columns']), "number of rows")
        st.session_state['turbineDiameter'] = st.selectbox(
            "Choose the diameter of the turbines",
            (10,20,30,40), index=None, placeholder="Select diameter..."
        )
        st.write('You selected:', str(st.session_state['turbineDiameter']), "meters.")
        st.session_state['turbineTipClearence'] = st.selectbox(
            "Choose the distance between turbine tips",
            (1,2,3), index=None, placeholder="Select clearence..."
        )
        st.write('You selected:', str(st.session_state['turbineTipClearence']), "meters.")

        max_capasity = 1500
        if st.session_state['rows'] != None and st.session_state['columns'] != None:
            st.session_state['n_mrs'] = max_capasity // (st.session_state['rows'] * st.session_state['columns'])
            st.write('The capasity at',option,'with',str(st.session_state['rows']),'amount of rows, and',str(st.session_state['columns']),'amount of columns, is ',str(st.session_state['n_mrs']),'Multi Rotor Systems')

        if st.button("Optimize Wind Farm"):
            minimumDistance = MinimumDistanceMultiRotor(st.session_state['f'],st.session_state['A'],st.session_state['k'], st.session_state['wd'], st.session_state['rows'], st.session_state['columns'])
            st.write("The minimum distance between multi rotors should be: ", str(minimumDistance))
            with st.spinner('Wait for it...'):
                st.session_state['state'], st.session_state['AEP'] = positionMultiRotor(boundaries, minimumDistance, st.session_state['n_mrs'], st.session_state['f'], st.session_state['A'], st.session_state['k'], st.session_state['wd'], ti, st.session_state['turbineDiameter'], st.session_state['turbineTipClearence'], st.session_state['columns'], st.session_state['rows'])

                y_coords = st.session_state['state']['x']
                x_coords = st.session_state['state']['y']
                
                plotMAP(x_coords,y_coords)
                st.write(st.session_state['state'])

                st.subheader('The expected AEP is '+str(st.session_state['AEP'])+'GWH')
                print(st.session_state['AEP'])

    elif option == 'Utsira Nord' and rotorType == 'Single Rotor':
        latitude, longitude = 59.4822222, 4.6736111
        boundaries = [(6590740.850, 572781.322),(6593647.566, 588120.311), (6582906.767, 590605.006), (6579871.157, 574182.456), (6585694.303, 572981.696)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        n_wt = 33
        st.write('The capasity at',option,'is',str(n_wt),'turbines')

        if st.button("Optimize Wind Farm"):
            with st.spinner('Wait for it...'):
                st.session_state['initial'], st.session_state['state'], aep_values = optimizeSingleTurbines(boundaries, n_wt, 1000, st.session_state['f'], st.session_state['A'], st.session_state['k'])
                
                plotAEP(aep_values)
                y_coords = st.session_state['state']['x']
                x_coords = st.session_state['state']['y']
                plotMAP(x_coords,y_coords)

    elif option == 'Utsira Nord' and rotorType == 'Multi Rotor':
        latitude, longitude = 59.4822222, 4.6736111
        boundaries = [(6590740.850, 572781.322),(6593647.566, 588120.311), (6582906.767, 590605.006), (6579871.157, 574182.456), (6585694.303, 572981.696)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        st.session_state['wd'] = np.linspace(0, 360, len(st.session_state['f']), endpoint=False)
        ti = 0.1

        st.session_state['rows'] = st.selectbox(
            "Choose how many rows the multi rotor systems will include",
            (2,3,4,5,6,7,8), index=None, placeholder="Select number rows..."
        )
        st.write('You selected:', str(st.session_state['rows']), "number of rows")
        st.session_state['columns'] = st.selectbox(
            "Choose how many columns the multi rotor systems will include",
            (2,3,4,5,6,7,8), index=None, placeholder="Select number columns..."
        )
        st.write('You selected:', str(st.session_state['columns']), "number of rows")
        st.session_state['turbineDiameter'] = st.selectbox(
            "Choose the diameter of the turbines",
            (10,20,30,40), index=None, placeholder="Select diameter..."
        )
        st.write('You selected:', str(st.session_state['turbineDiameter']), "meters.")
        st.session_state['turbineTipClearence'] = st.selectbox(
            "Choose the distance between turbine tips",
            (1,2,3), index=None, placeholder="Select clearence..."
        )
        st.write('You selected:', str(st.session_state['turbineTipClearence']), "meters.")

        max_capasity = 500
        if st.session_state['rows'] != None and st.session_state['columns'] != None:
            st.session_state['n_mrs'] = max_capasity // (st.session_state['rows'] * st.session_state['columns'])
            st.write('The capasity at',option,'with',str(st.session_state['rows']),'amount of rows, and',str(st.session_state['columns']),'amount of columns, is ',str(st.session_state['n_mrs']),'Multi Rotor Systems')

        if st.button("Optimize Wind Farm"):
            minimumDistance = MinimumDistanceMultiRotor(st.session_state['f'],st.session_state['A'],st.session_state['k'], st.session_state['wd'], st.session_state['rows'], st.session_state['columns'])
            st.write("The minimum distance between multi rotors should be: ", str(minimumDistance))
            with st.spinner('Wait for it...'):
                st.session_state['state'], st.session_state['AEP'] = positionMultiRotor(boundaries, minimumDistance, st.session_state['n_mrs'], st.session_state['f'], st.session_state['A'], st.session_state['k'], st.session_state['wd'], ti, st.session_state['turbineDiameter'], st.session_state['turbineTipClearence'], st.session_state['columns'], st.session_state['rows'])

                y_coords = st.session_state['state']['x']
                x_coords = st.session_state['state']['y']
                
                plotMAP(x_coords,y_coords)
                st.write(st.session_state['state'])

                st.subheader('The expected AEP is '+str(st.session_state['AEP'])+'GWH')
                print(st.session_state['AEP'])
            
            

            
            
    

if __name__ == "__main__":
    main()

# streamlit run --server.fileWatcherType=poll streamlit.py
# streamlit run streamlit.py
