import sys
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

sys.path.append('../')
from Bearing_defect_simulation.DES.Simulation import Simulation
from Bearing_defect_simulation.Bearing.Bearing import Bearing
from Bearing_defect_simulation.Bearing.RollingElement import RollingElement
from Bearing_defect_simulation.DES.Acquisition import Acquisition

def run_simulation(a_n, a_dP, a_race, a_rpm,
                   a_dB, a_theta, a_L, a_N,
                   a_lambda, a_delta,
                   a_duration, a_frequency, a_noise):
    try:
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
        results = my_simulation.get_results(format='show')
      
        if results is None or len(results) != 2:
            st.error("Simulation returned invalid results.")
            return None

        t, x = results
        fig, ax = plt.subplots()
        ax.plot(t, x, linewidth=1)
        ax.set_title("Simulated Bearing Vibration Signal")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
        return fig

    except Exception as e:
        st.error(f"Simulation failed inside run_simulation: {e}")
        return None

def main():
    st.title("🔧 Bearing Defect Vibration Simulation")

    # Define presets
    presets = {
        "CWRU": {
            "a_n": 9, "a_dP": 71.5, "a_race": "outer", "a_rpm": 1772,
            "a_dB": 8.4074, "a_theta": 15.0, "a_L": 3.8, "a_N": 3,
            "a_lambda": "0.7 0.7 0.7", "a_delta": "0.5 0.5 0.5",
            "a_duration": 1.0, "a_frequency": 12000.0, "a_noise": 0.05
        },
        "NASA": {
            "a_n": 8, "a_dP": 50.0, "a_race": "inner", "a_rpm": 2000,
            "a_dB": 7.0, "a_theta": 15.0, "a_L": 3.0, "a_N": 4,
            "a_lambda": "0.6 0.7 0.6 0.7", "a_delta": "0.4 0.4 0.5 0.5",
            "a_duration": 1.0, "a_frequency": 20000.0, "a_noise": 0.1
        },
        "Paderborn": {
            "a_n": 16, "a_dP": 100.0, "a_race": "outer", "a_rpm": 1500,
            "a_dB": 10.0, "a_theta": 20.0, "a_L": 4.0, "a_N": 5,
            "a_lambda": "0.8 0.8 0.8 0.8 0.8", "a_delta": "0.3 0.4 0.5 0.6 0.7",
            "a_duration": 1.0, "a_frequency": 64000.0, "a_noise": 0.1
        }
    }

    if dataset != "Custom":
        preset = presets[dataset]
    else:
        preset = {
            "a_n": 16, "a_dP": 71.501, "a_race": "outer", "a_rpm": 2000,
            "a_dB": 8.4074, "a_theta": 15.17, "a_L": 3.8, "a_N": 5,
            "a_lambda": "0.7 0.7 0.8 0.8 0.8", "a_delta": "0.5 0 0.5 0 0.7",
            "a_duration": 1.0, "a_frequency": 48000.0, "a_noise": 0.1
        }

    with st.sidebar:
      
        # Dataset preset selector
        st.header("Select Dataset Preset")
        dataset = st.radio("Choose a public dataset:", options=["Custom", "CWRU", "NASA", "Paderborn"])

        st.header("Simulation Parameters")
        a_n = st.number_input("Number of rolling elements (n)", min_value=1, value=preset["a_n"])
        a_dP = st.number_input("Pitch diameter (dP) [mm]", value=preset["a_dP"])
        a_race = st.selectbox("Defect on race", options=["inner", "outer"], index=0 if preset["a_race"] == "inner" else 1)
        a_rpm = st.number_input("Rotational speed (rpm)", value=preset["a_rpm"])
        a_dB = st.number_input("Rolling element diameter (dB) [mm]", value=preset["a_dB"])
        a_theta = st.number_input("Contact angle (θ) [deg]", value=preset["a_theta"])
        a_L = st.number_input("Defect length (L) [mm]", value=preset["a_L"])
        a_N = st.number_input("Number of intervals (N)", min_value=1, value=preset["a_N"])
        a_lambda_str = st.text_input("Defect lengths (λ) [space-separated]", value=preset["a_lambda"])
        a_delta_str = st.text_input("Defect depths (δ) [space-separated]", value=preset["a_delta"])
        a_duration = st.number_input("Duration (s)", value=preset["a_duration"])
        a_frequency = st.number_input("Frequency (Hz)", value=preset["a_frequency"])
        a_noise = st.slider("Noise level", min_value=0.0, max_value=0.9, value=preset["a_noise"])

    if st.button("Run Simulation"):
        try:
            # Safely parse and define these inside the button block
            a_lambda = np.array([float(x) for x in a_lambda_str.strip().split()])
            a_delta = np.array([float(x) for x in a_delta_str.strip().split()])

            if len(a_lambda) != a_N or len(a_delta) != a_N:
                st.error(f"Mismatch: Length of λ = {len(a_lambda)}, δ = {len(a_delta)}; but N = {a_N}")
                return

            fig = run_simulation(
                a_n, a_dP, a_race, a_rpm,
                a_dB, a_theta, a_L, a_N,
                a_lambda, a_delta,
                a_duration, a_frequency, a_noise
            )
            if fig:
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Simulation failed outside: {e}")

if __name__ == "__main__":
    main()
