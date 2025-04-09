import sys
import math
import numpy as np
import time

import streamlit as st
import matplotlib.pyplot as plt

from Bearing_defect_simulation.Bearing.Bearing import Bearing
from Bearing_defect_simulation.Bearing.RollingElement import RollingElement
from Bearing_defect_simulation.DES.Acquisition import Acquisition

class Simulation:
    def __init__(self, bearing: Bearing, acquisition: Acquisition):
        if bearing.m_outerRace:
            self.m_n_ball_to_pass = round(acquisition.m_duration * bearing.get_BPFO_freq())
        else:
            self.m_n_ball_to_pass = round(acquisition.m_duration * bearing.get_BPFI_freq())

        self.m_ballList = [RollingElement(bearing.m_dB, bearing.m_duration) for _ in range(self.m_n_ball_to_pass)]
        self.m_bearing = bearing
        self.m_acquisition = acquisition
        self.m_gamma = 10
        self.m_waveform = np.zeros(acquisition.m_waveform.shape)

    def run_ball_through_defect(self, i: int, ball: RollingElement):
        time_enter_defect = i * self.m_bearing.m_duration_between_ball
        time_exit_defect = time_enter_defect + ball.m_duration
        dx = self.m_acquisition.m_dt / ball.m_duration * self.m_bearing.m_defect.m_L
        dt = time_enter_defect

        while dt < time_exit_defect:
            dt += self.m_acquisition.m_dt
            ball.advance(dx)
            interval_underball = self.find_interval_under_ball(ball, i)
            if interval_underball:
                amplitude = self.get_amplitude(ball, interval_underball)
                position_in_array = self.get_position_pulse_in_waveform(time_enter_defect, dt)
                self.m_waveform[position_in_array] = amplitude

        # Debugging: Print the waveform's first few values after running a ball through the defect
        if i == self.m_n_ball_to_pass - 1:
            st.write("First 10 values of m_waveform after ball simulation:")
            st.write(self.m_waveform[:10])
            
        return 0

    def find_interval_under_ball(self, ball: RollingElement, j: int):
        # Check all intervals to see which one the ball is in and if it's high enough to contact
        for k in range(len(self.m_bearing.m_defect.m_x_pos_filtered)):
            ball_position = ball.m_x_pos_in_defect
            begin_interval = self.m_bearing.m_defect.m_x_pos_filtered[k]
            end_interval = begin_interval + self.m_bearing.m_defect.m_lambda_filtered[k]

            if begin_interval < ball_position < end_interval:
                if k not in ball.m_index_interval_touched:
                    ball.m_index_interval_touched.append(k)
                    return k, self.m_bearing.m_defect.m_index_filtered[k]
        return 0

    def get_amplitude(self, ball: RollingElement, interval_underball: tuple):
        pos_current_contact_interval = self.m_bearing.m_defect.m_x_pos_filtered[interval_underball[0]]
        if interval_underball[0] - 1 >= 0:
            pos_previous_contact_interval = self.m_bearing.m_defect.m_x_pos_filtered[interval_underball[0] - 1] + self.m_bearing.m_defect.m_lambda_filtered[interval_underball[0] - 1]
            amplitude = self.m_gamma * (pos_current_contact_interval - pos_previous_contact_interval)
            return amplitude
        else:
            amplitude = self.m_gamma * (pos_current_contact_interval)
            return amplitude

    def get_position_pulse_in_waveform(self, time_enter_defect, dt):
        return int((dt / self.m_acquisition.m_dt))

    def start(self):
        time_start = time.time()
        for i, ball in enumerate(self.m_ballList):
            self.run_ball_through_defect(i, ball)

        # Debugging: Check the final waveform data
        st.write("Simulation completed. First 10 values of m_waveform:")
        st.write(self.m_acquisition.m_waveform[:10])

        noise = np.random.normal(0, self.m_acquisition.m_noise * max(self.m_acquisition.m_waveform), self.m_acquisition.m_waveform.shape)
        self.m_acquisition.m_waveform += noise
        st.write("Simulation completed in {:.4f}s.".format(time.time() - time_start))

    def get_results(self, format='show', file_name='results.png', title="Simulated Spectrum"):
        # Get the FFT and plot the results
        fft_res = self.m_acquisition.get_fft()
        x = fft_res[0][:int(self.m_acquisition.m_frequency / 10)]
        y = fft_res[1][:int(self.m_acquisition.m_frequency / 10)]

        if format == 'show':
            st.write(title)
            fig, ax = plt.subplots()
            ax.plot(x, y, color='red')
            ax.set_title(title)
            ax.set_xlabel("Freq (Hz)")
            ax.set_ylabel("Amplitude")
            st.pyplot(fig)

        elif format == 'as_array':
            st.write("Output formatted as array:")
            st.write(self.m_acquisition.m_spectrum)

        elif format == 'as_file':
            st.write('Output formatted as file')
            plt.figure()
            plt.plot(x, y)
            plt.savefig(file_name)
            st.write(f"Results saved as {file_name}")

        else:
            st.write("Err: format unknown")

    def get_info(self):
        self.m_bearing.get_info()
        self.m_acquisition.get_info()
        st.write("################# SIMULATION PARAMS ################## ")
        st.write("Simulation created")
        st.write("Number of balls to pass on the defect: " + str(self.m_n_ball_to_pass))
        st.write("######################################################## ")

