from pyproj import Proj, transform
from streamlit_folium import folium, folium_static
import streamlit as st

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

folium.PolyLine(utsira_koordinater, tooltip="Utsira Nord").add_to(m)
folium.PolyLine(SNii_koordinater, tooltip="Sørlige Norsjø II").add_to(m)

def add_markers(points):
        for lat, lon in points:
            folium.Marker(location=[lat, lon], popup="Single turbine").add_to(m)

def plotMAP(x_coords,y_coords):

    # Define the coordinate systems (Cartesian and WGS 84)
    cartesian = Proj(init='epsg:32631')  # Assuming the coordinates are in UTM Zone 31N
    wgs84 = Proj(init='epsg:4326')  # WGS 84

    # Convert Cartesian coordinates to latitude and longitude
    lon, lat = transform(cartesian, wgs84, x_coords, y_coords)


    points = list(zip(lat, lon))
    add_markers(points)
    folium_static(m)