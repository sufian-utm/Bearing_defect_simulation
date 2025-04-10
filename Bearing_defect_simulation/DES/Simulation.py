import sys
import math
import numpy as np
import time
from threading import Thread

import streamlit as st
import matplotlib.pyplot as plt

sys.path.append('../')
from Bearing_defect_simulation.Bearing.Bearing import Bearing
from Bearing_defect_simulation.Bearing.RollingElement import RollingElement
from Bearing_defect_simulation.DES.Acquisition import Acquisition


class Simulation(object):
    """
    The main simulation engine
    """
    def __init__(self, bearing: Bearing, acquisition: Acquisition):
        if bearing.outer:
            self.m_n_ball_to_pass = round(acquisition.m_duration * bearing.get_BPFO_freq())
        else:
            self.m_n_ball_to_pass = round(acquisition.m_duration * bearing.get_BPFI_freq())

        self.m_ballList = [RollingElement(bearing.m_dB, bearing.m_duration)
                           for i in range(self.m_n_ball_to_pass)]
        self.m_bearing = bearing
        self.m_acquisition = acquisition
        self.m_gamma = 10

        self.m_threads = []
        for i, ball in enumerate(self.m_ballList):
            self.m_threads.append(Thread(target=self.run_ball_throught_defect, args=(i, ball)))
        self.get_info()

    def run_ball_throught_defect(self, i: int, ball: RollingElement):
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
                self.m_acquisition.m_waveform[position_in_array] = amplitude
        return 0

    def get_position_pulse_in_waveform(self, time_enter_defect, dt):
        return int((dt / self.m_acquisition.m_dt))

    def get_amplitude(self, ball: RollingElement, interval_underball: tuple):
        pos_current = self.m_bearing.m_defect.m_x_pos_filtered[interval_underball[0]]
        if interval_underball[0] - 1 >= 0:
            pos_prev = self.m_bearing.m_defect.m_x_pos_filtered[interval_underball[0] - 1] + \
                       self.m_bearing.m_defect.m_lambda_filtered[interval_underball[0] - 1]
            amplitude = self.m_gamma * (pos_current - pos_prev)
        else:
            amplitude = self.m_gamma * pos_current
        return amplitude

    def find_interval_under_ball(self, ball: RollingElement, j):
        for k in range(len(self.m_bearing.m_defect.m_x_pos_filtered)):
            ball_pos = ball.m_x_pos_in_defect
            begin = self.m_bearing.m_defect.m_x_pos_filtered[k]
            end = begin + self.m_bearing.m_defect.m_lambda_filtered[k]

            if begin < ball_pos < end:
                if k not in ball.m_index_interval_touched:
                    ball.m_index_interval_touched.append(k)
                    return (k, self.m_bearing.m_defect.m_index_filtered[k])
            if begin == self.m_bearing.m_defect.m_L and begin < ball_pos:
                return (k, self.m_bearing.m_defect.m_index_filtered[k])
        return 0

    def start(self):
        time_start = time.time()
        for t in self.m_threads:
            t.start()
        for t in self.m_threads:
            t.join()
        noise = np.random.normal(0,
                                 self.m_acquisition.m_noise * max(self.m_acquisition.m_waveform),
                                 self.m_acquisition.m_waveform.shape)
        self.m_acquisition.m_waveform += noise
        st.success(f"Simulation completed in {time.time() - time_start:.4f}s.")

    def get_results(self, format: str, file_name='results.png', title="Simulated Spectrum"):
        fft_res = self.m_acquisition.get_fft()
        x = fft_res[0][:int(self.m_acquisition.m_frequency / 10)]
        y = fft_res[1][:int(self.m_acquisition.m_frequency / 10)]

        if format == 'as_array':
            st.subheader("Output formatted as array")
            return np.linspace(0, self.m_acquisition.m_duration, self.m_acquisition.m_waveform_len), \
                   self.m_acquisition.m_waveform

        elif format == 'as_file':
            plt.figure()
            plt.title(title)
            plt.xlabel("Freq (Hz)")
            plt.ylabel("Amplitude")
            plt.plot(x, y, color="red")
            plt.savefig(file_name)
            st.success(f"Saved spectrum to `{file_name}`")

        elif format == 'as_graph' or format == 'show':
            fig, ax = plt.subplots()
            ax.plot(x, y, color="red")
            ax.set_title(title)
            ax.set_xlabel("Freq (Hz)")
            ax.set_ylabel("Amplitude")
            st.pyplot(fig)

            time_axis = np.linspace(0, self.m_acquisition.m_duration, self.m_acquisition.m_waveform_len)
            amplitude = self.m_acquisition.m_waveform
            return time_axis, amplitude 

        else:
            st.error("Err: Unknown format in get_results()")

    def get_info(self):
        self.m_bearing.get_info()
        self.m_acquisition.get_info()
        st.markdown("### 🛠️ Simulation Parameters")
        st.write(f"**Number of balls to pass on the defect**: {self.m_n_ball_to_pass}")
