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
        if bearing.m_outerRace:
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
        dx = self.m_acquisition.m_dt /
