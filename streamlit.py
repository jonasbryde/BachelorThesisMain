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
from MinimumDistanceMultiRotor import MinimumDistanceMultiRotor
from optimizeSingleTurbines import optimizeSingleTurbines
from positionMultiRotor import positionMultiRotor
from PerformWindAnalysis import perform_wind_analysis
from pyproj import Proj, transform
import ast
import time
from plotAEP import plotAEP
from plotMap import plotMAP

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
        boundaries = [(6298528.997, 582191.366), (6329862.416, 631362.055), (6291012.798, 652762.909), (6273783.939, 624877.085), (6261144.506, 601081.704)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        n_wt = 10
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
        boundaries = [(6298528.997, 582191.366), (6329862.416, 631362.055), (6291012.798, 652762.909), (6273783.939, 624877.085), (6261144.506, 601081.704)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        st.session_state['wd'] = np.linspace(0, 360, len(st.session_state['f']), endpoint=False)

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

        max_capasity = 500
        if st.session_state['rows'] != None and st.session_state['columns'] != None:
            st.session_state['n_mrs'] = max_capasity // (st.session_state['rows'] * st.session_state['columns'])
            st.write('The capasity at',option,'with',str(st.session_state['rows']),'amount of rows, and',str(st.session_state['columns']),'amount of columns, is ',str(st.session_state['n_mrs']),'Multi Rotor Systems')

        if st.button("Optimize Wind Farm"):
            minimumDistance = MinimumDistanceMultiRotor(st.session_state['f'],st.session_state['A'],st.session_state['k'], st.session_state['wd'], st.session_state['rows'], st.session_state['columns'])
            st.write("The minimum distance between multi rotors should be: ", str(minimumDistance))
            st.session_state['state'] = positionMultiRotor(boundaries, minimumDistance, st.session_state['n_mrs'])

            y_coords = st.session_state['state']['x']
            x_coords = st.session_state['state']['y']
            st.write(st.session_state['state'])

            plotMAP(x_coords,y_coords)



    elif option == 'Utsira Nord' and rotorType == 'Single Rotor':
        latitude, longitude = 59.4822222, 4.6736111
        boundaries = [(6590631.429, 571964.171), (6548635.029, 580697.416), (6553152.617, 603791.015), (6594942.605, 594798.438)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        n_wt = 10
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
        boundaries = [(6590631.429, 571964.171), (6548635.029, 580697.416), (6553152.617, 603791.015), (6594942.605, 594798.438)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)

        st.session_state['wd'] = np.linspace(0, 360, len(st.session_state['f']), endpoint=False)

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

        max_capasity = 500
        if st.session_state['rows'] != None and st.session_state['columns'] != None:
            st.session_state['n_mrs'] = max_capasity // (st.session_state['rows'] * st.session_state['columns'])
            st.write('The capasity at',option,'with',str(st.session_state['rows']),'amount of rows, and',str(st.session_state['columns']),'amount of columns, is ',str(st.session_state['n_mrs']),'Multi Rotor Systems')

        if st.button("Optimize Wind Farm"):
            minimumDistance = MinimumDistanceMultiRotor(st.session_state['f'],st.session_state['A'],st.session_state['k'], st.session_state['wd'], st.session_state['rows'], st.session_state['columns'])
            st.write("The minimum distance between multi rotors should be: ", str(minimumDistance))
            st.session_state['state'] = positionMultiRotor(boundaries, minimumDistance, st.session_state['n_mrs'])

            y_coords = st.session_state['state']['x']
            x_coords = st.session_state['state']['y']
            st.write(st.session_state['state'])
                
            plotMAP(x_coords,y_coords)
            
    

if __name__ == "__main__":
    main()

# streamlit run --server.fileWatcherType=poll streamlit.py
# streamlit run streamlit.py
