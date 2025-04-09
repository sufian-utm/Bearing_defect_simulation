import numpy as np
from scipy import fft, ifft
import streamlit as st
import matplotlib.pyplot as plt

class Signal(object):
    """
    Signal class
    """
    def __init__(self, a_waveform_len: int, a_waveform: np.ndarray,
                 a_time_resolution: float, a_spectrum: np.ndarray):
        self.m_waveform_len = a_waveform_len
        self.m_waveform = a_waveform  # Store the waveform passed in initialization
        self.m_time_resolution = a_time_resolution
        self.m_spectrum = a_spectrum

    def get_fft(self):
        """
        Compute the Fast Fourier Transform (FFT) of the waveform.
        """
        self.m_spectrum = fft.fft(self.m_waveform)  # Corrected FFT computation
        return self.m_spectrum

    def get_ifft(self):
        """
        Compute the Inverse Fast Fourier Transform (IFFT) of the spectrum.
        """
        if self.m_spectrum.size == 0:
            st.write("Error: Spectrum is empty. Please compute FFT first.")
        else:
            inverse_spectrum = ifft.ifft(self.m_spectrum)
            st.write("Inverse FFT calculated.")
            return inverse_spectrum

    def plot_waveform(self):
        """
        Plot the time-domain waveform using Streamlit.
        """
        fig, ax = plt.subplots()
        ax.plot(np.arange(self.m_waveform_len) * self.m_time_resolution, self.m_waveform)
        ax.set_title("Time Domain Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        st.pyplot(fig)

    def plot_spectrum(self):
        """
        Plot the frequency-domain spectrum using Streamlit.
        """
        if self.m_spectrum.size == 0:
            st.write("Error: Spectrum is empty. Please compute FFT first.")
        else:
            freq = np.fft.fftfreq(self.m_waveform_len, d=self.m_time_resolution)
            fig, ax = plt.subplots()
            ax.plot(freq[:self.m_waveform_len // 2], np.abs(self.m_spectrum)[:self.m_waveform_len // 2])
            ax.set_title("Frequency Domain Spectrum")
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel("Amplitude")
            st.pyplot(fig)
