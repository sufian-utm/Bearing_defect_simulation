import sys
import math
import numpy as np
from typing import Tuple

class Acquisition(object):
    """
    Acquisition class, represents the simulation time discretization
    """
    def __init__(self, a_duration: float = 1, a_frequency: float = 20000, a_noise: float = 0.1):
        self.m_duration = a_duration  # Duration of the acquisition in (s)
        self.m_frequency = a_frequency  # Frequency of acquisition in (Hz)
        self.m_dt = 1 / a_frequency  # Time between 2 sampling points 1/m_frequency (s)
        self.m_noise = a_noise  # Noise parameter in the waveform
        # Attributes related to the vibration signal
        self.m_waveform_len = round(self.m_duration * self.m_frequency)
        self.m_waveform = np.zeros(self.m_waveform_len)
        self.m_spectrum = np.array([])

    def get_fft(self):
        """Generate and return the FFT of the waveform."""
        self.m_spectrum = self.generate_fft()
        return self.m_spectrum

    def generate_fft(self):
        """Generate the FFT of the waveform."""
        fourierTransform = np.fft.fft(self.m_waveform) / len(self.m_waveform)  # Normalize amplitude
        fourierTransform = fourierTransform[range(int(len(self.m_waveform) / 2))]  # Exclude sampling frequency
        tpCount = len(self.m_waveform)
        values = np.arange(int(tpCount / 2))
        timePeriod = tpCount / self.m_frequency
        frequencies = values / timePeriod
        return (frequencies, abs(fourierTransform))

    def get_info(self):
        """Print information about the acquisition parameters."""
        print("################# ACQUISITION PARAM  ############## ")
        print("#")
        print(f"#  Duration: {self.m_duration}s")
        print(f"#  Frequency: {self.m_frequency}Hz")
        print(f"#  Time resolution: {round(1000000 * self.m_dt) / 1000000}s")
        print(f"#  Number of signal's points: {self.m_waveform_len}")
        print("#")

    def debug_waveform(self):
        """Print some debugging information about the waveform."""
        print(f"Waveform sample data (first 10 points): {self.m_waveform[:10]}")
        print(f"Waveform last 10 points: {self.m_waveform[-10:]}")
