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



def main():


    st.title("Wind analysis and wind turbine optimization")

    st.write('''OsloMET Bachelor thesis, v24: Group 6''')
    # Create a default map showing the wind farm areas
    m = folium.Map(location=[59.0, 5.11], zoom_start=6)

    #Markerer boundary for vindområdene
    utsira_koordinater = [
    (59.4480556, 4.2691667),
    (59.0694444, 4.4075),
    (59.105, 4.8122222),
    (59.4822222, 4.6736111),
    (59.4480556, 4.2691667),]

    SNii_koordinater = [
    (56.8233333,4.3466667),
    (57.0933333,5.1680556),
    (56.7380556,5.4975),
    (56.5916667,5.0336111),
    (56.4838889,4.6413889),
    (56.8233333,4.3466667),]

    #Hvor stor periode skal vinddataen analysere
    #start_date = st.date_input("Enter start date:")
    #end_date = st.date_input("Enter end date:")
    start_date_formatted = 20180101
    end_date_formatted = 20230101

    folium.PolyLine(utsira_koordinater, tooltip="Utsira Nord").add_to(m)
    folium.PolyLine(SNii_koordinater, tooltip="Sørlige Norsjø II").add_to(m)

    folium_static(m)

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
    
        

    option = st.selectbox(
    "What area do you want to analyze?",
    ("Utsira Nord", "Sørlige Nordsjø II"),index=None, placeholder="Select area...",)
    st.write('You selected:', option)

    if option == 'Utsira Nord':
        latitude, longitude = 59.4822222, 4.6736111
        boundaries = [(6590631.429, 571964.171), (6548635.029, 580697.416), (6553152.617, 603791.015), (6594942.605, 594798.438)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)
        print(st.session_state['f'])

    elif option == 'Sørlige Nordsjø II':
        latitude, longitude = 56.8233333, 4.3466667
        boundaries = [(6298528.997, 582191.366), (6329862.416, 631362.055), (6291012.798, 652762.909), (6273783.939, 624877.085), (6261144.506, 601081.704)]
        constraint = XYBoundaryConstraint(boundaries, 'polygon')
        st.session_state['f'], st.session_state['A'], st.session_state['k'] = perform_wind_analysis(option, latitude, longitude, start_date_formatted, end_date_formatted)
        print(st.session_state['f'])
    


    rotorType = st.selectbox(
        "Choose wind turbine type",
        ("Single Rotor", "Multi Rotor"), index=None, placeholder="Select turbine type..."
    )
    st.write('You selected:', rotorType)

    if rotorType == "Multi Rotor":
        wd = np.linspace(0, 360, len(st.session_state['f']), endpoint=False)
        ti = 0.1
        site = XRSite(ds = xr.Dataset(data_vars={'Sector_frequency': ('wd', st.session_state['f']), 'Weibull_A': ('wd', st.session_state['A']), 'Weibull_k': ('wd', st.session_state['k']), 'TI': ti},
                        coords={'wd': wd}))

        #Defining the wind turbine object
        u = [0,3,12,25,30]
        ct = [0,8/9,8/9,.3, 0]
        power = [0,0,1000,1000,0]

        wind_turbines = WindTurbine(name='MyWT',
                            diameter=30,
                            hub_height=40,
                            powerCtFunction=PowerCtTabular(u,power,'kW',ct))
        
        wfmodel = NOJ(site, wind_turbines)

        rows = st.selectbox(
            "Choose how many rows the multi rotor systems will include",
            (2,3,4,5,6,7,8), index=None, placeholder="Select number rows..."
        )
        st.write('You selected:', str(rows), "number of rows")
        collumns = st.selectbox(
            "Choose how many rows the multi rotor systems will include",
            (2,3,4,5,6,7,8), index=None, placeholder="Select number collumns..."
        )
        st.write('You selected:', str(collumns), "number of rows...")
    elif rotorType == "Single Rotor":
        
        wd = np.linspace(0, 360, len(st.session_state['f']), endpoint=False)
        ti = 0.1
        site = XRSite(ds = xr.Dataset(data_vars={'Sector_frequency': ('wd', st.session_state['f']), 'Weibull_A': ('wd', st.session_state['A']), 'Weibull_k': ('wd', st.session_state['k']), 'TI': ti},
                        coords={'wd': wd}))
        

        #Defining the wind turbine object
        u = [0,3,12,25,30]
        ct = [0,8/9,8/9,.3, 0]
        power = [0,0,15000,15000,0]

        wind_turbines = WindTurbine(name='MyWT',
                            diameter=240,
                            hub_height=150,
                            powerCtFunction=PowerCtTabular(u,power,'kW',ct))

        wfmodel = NOJ(site, wind_turbines)
    
    def add_markers(points):
        for lat, lon in points:
            folium.Marker(location=[lat, lon], popup="Single turbine").add_to(m)

    # Button to trigger optimization
    if st.button("Optimize Wind Farm"):
        if rotorType == 'Single Rotor':
            if option == 'Sørlige Norsjø II':
                n_wt = 100
            elif option == 'Utsira Nord':
                n_wt = 33
            st.write('The capasity at',option,'is',str(n_wt),'turbines')
            with st.spinner('Wait for it...'):
                st.session_state['initial'], st.session_state['state'], aep_values = optimizeSingleTurbines(boundaries, n_wt, 1000, st.session_state['f'], st.session_state['A'], st.session_state['k'])
                aep_plot=aep_values[0]
                aep_plot=aep_plot.tolist()
                x_values = []
                for i in range(len(aep_plot)):   
                    x_values.append(i)
                print(x_values)
                print()
                print()
                print(aep_plot)
                plt.figure(figsize=(10, 6))
                plt.plot(x_values, aep_plot, marker='o', linestyle='-')
                plt.xlabel('Iteration number')
                plt.ylabel('AEP (GWh)')
                plt.title('AEP over iterations')
                plt.grid(True)

                # Display the plot in Streamlit
                st.pyplot(plt)
                y_coords = st.session_state['state']['x']
                x_coords = st.session_state['state']['y']
                st.write(st.session_state['state'])
                #print(x_coords, y_coords)


                # Define the coordinate systems (Cartesian and WGS 84)
                cartesian = Proj(init='epsg:32631')  # Assuming the coordinates are in UTM Zone 31N
                wgs84 = Proj(init='epsg:4326')  # WGS 84

                # Convert Cartesian coordinates to latitude and longitude
                lon, lat = transform(cartesian, wgs84, x_coords, y_coords)

                # Now, you have the latitude and longitude coordinates
                #print("Latitude:", lat)
                #print("Longitude:", lon)

                points = list(zip(lat, lon))
                add_markers(points)
                folium_static(m)


            st.success('Done!')
            

        elif rotorType == 'Multi Rotor':

            if option == 'Sørlige Norsjø II':
                max_capasity = 1500
                n_mrs = max_capasity // (rows * collumns)
            elif option == 'Utsira Nord':
                max_capasity = 500
                n_mrs = max_capasity // (rows * collumns)
            st.write('The capasity at',option,'with',str(rows),'amount of rows, and',str(collumns),'amount of columns, is ',str(n_mrs),'Multi Rotor Systems')
            
            #Optimize according to multi Rotor
            minimumDistance = MinimumDistanceMultiRotor(st.session_state['f'],st.session_state['A'],st.session_state['k'], wd, rows, collumns)
            st.write("The minimum distance between multi rotors should be: ", str(minimumDistance))
            st.session_state['state'] = positionMultiRotor(boundaries, minimumDistance, n_mrs)

            y_coords = st.session_state['state']['x']
            x_coords = st.session_state['state']['y']
            st.write(st.session_state['state'])
                
            # Define the coordinate systems (Cartesian and WGS 84)
            cartesian = Proj(init='epsg:32631')  # Assuming the coordinates are in UTM Zone 31N
            wgs84 = Proj(init='epsg:4326')  # WGS 84

            # Convert Cartesian coordinates to latitude and longitude
            lon, lat = transform(cartesian, wgs84, x_coords, y_coords)


            points = list(zip(lat, lon))
            add_markers(points)
            folium_static(m)

    

if __name__ == "__main__":
    main()

# streamlit run --server.fileWatcherType=poll streamlit.py
# streamlit run streamlit.py
