import streamlit as st
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

sys.path.append('../')
from Bearing_defect_simulation.DES.Simulation import Simulation
from Bearing_defect_simulation.Bearing.Bearing import Bearing
from Bearing_defect_simulation.DES.Acquisition import Acquisition
from your_simulation_file import Simulation  # Import your Simulation class

def run_simulation(a_n:int, a_dP:float, a_race:str, a_rpm:int,
                   a_dB:float, a_theta:float, a_L:float, a_N:int,
                   a_lambda:np.ndarray, a_delta:np.ndarray,
                   a_duration:float, a_frequency:float, a_noise:float):
    """
    Run the simulation and return a matplotlib figure
    """
    my_bearing = Bearing(
        a_n=a_n, a_dP=a_dP, a_race=a_race,
        a_rpm=a_rpm, a_dB=a_dB, a_theta=a_theta,
        a_L=a_L, a_N=a_N, a_lambda=a_lambda, a_delta=a_delta
    )

    my_acquisition = Acquisition(
        a_duration=a_duration,
        a_frequency=a_frequency,
        a_noise=a_noise
    )

    my_simulation = Simulation(my_bearing, my_acquisition)
    my_simulation.start()

    # Instead of relying on get_results, directly access attributes
    t = my_simulation.time
    x = my_simulation.signal

    if t is None or x is None:
        raise ValueError("Simulation did not generate time or signal data.")

    fig, ax = plt.subplots()
    ax.plot(t, x, linewidth=1)
    ax.set_title("Simulated Bearing Vibration Signal")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True)

    return fig

def main():
    st.title("🔧 Bearing Defect Vibration Simulation")

    with st.sidebar:
        st.header("Simulation Parameters")
        a_n = st.number_input("Number of rolling elements (n)", min_value=1, value=16)
        a_dP = st.number_input("Pitch diameter (dP) [mm]", value=71.501)
        a_race = st.selectbox("Defect on race", options=["inner", "outer"], index=1)
        a_rpm = st.number_input("Rotational speed (rpm)", value=2000)
        a_dB = st.number_input("Rolling element diameter (dB) [mm]", value=8.4074)
        a_theta = st.number_input("Contact angle (θ) [deg]", value=15.17)
        a_L = st.number_input("Defect length (L) [mm]", value=3.8)
        a_N = st.number_input("Number of intervals (N)", min_value=1, value=5)
        a_lambda = st.text_input("Defect lengths (λ) [space-separated]", value="0.7 0.7 0.8 0.8 0.8")
        a_delta = st.text_input("Defect depths (δ) [space-separated]", value="0.5 0 0.5 0 0.7")
        a_duration = st.number_input("Duration (s)", value=1.0)
        a_frequency = st.number_input("Frequency (Hz)", value=20000.0)
        a_noise = st.slider("Noise level", min_value=0.0, max_value=0.9, value=0.1)

    if st.button("Run Simulation"):
        try:
            lambda_arr = np.array([float(x) for x in a_lambda.strip().split()])
            delta_arr = np.array([float(x) for x in a_delta.strip().split()])

            fig = run_simulation(
                a_n=a_n, a_dP=a_dP, a_race=a_race, a_rpm=a_rpm,
                a_dB=a_dB, a_theta=a_theta, a_L=a_L, a_N=a_N,
                a_lambda=lambda_arr, a_delta=delta_arr,
                a_duration=a_duration, a_frequency=a_frequency,
                a_noise=a_noise
            )
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Simulation failed: {e}")

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
