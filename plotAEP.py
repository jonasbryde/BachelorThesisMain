import matplotlib.pyplot as plt
import streamlit as st

def plotAEP(aep_values):
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
