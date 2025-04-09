import streamlit as st
import numpy as np
from Bearing_defect_simulation.Bearing.Bearing import Bearing
from Bearing_defect_simulation.DES.Acquisition import Acquisition
from your_simulation_file import Simulation  # Import your Simulation class

def main():
    st.title("Bearing Defect Simulation")

    # Inputs for simulation
    n = st.slider("Number of Rolling Elements", 1, 50, 16)
    dP = st.slider("Pitch Diameter (mm)", 50.0, 100.0, 71.5)
    rpm = st.slider("RPM", 1000, 5000, 2000)
    race = st.selectbox("Race Affected", ["outer", "inner"])
    duration = st.number_input("Duration of Simulation (s)", min_value=1.0, value=1.0)
    frequency = st.number_input("Sampling Frequency (Hz)", min_value=1000, value=20000)
    noise = st.slider("Noise Level", 0.0, 1.0, 0.1)

    # Initialize bearing and acquisition objects
    bearing = Bearing(a_n=n, a_dP=dP, a_race=race, a_rpm=rpm)
    acquisition = Acquisition(a_duration=duration, a_frequency=frequency, a_noise=noise)

    # Create and run simulation
    sim = Simulation(bearing, acquisition)
    sim.start()

    # Display results
    sim.get_results(format="show")

if __name__ == "__main__":
    main()
