import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.signal import find_peaks

from Configuration_Files.configuration_4qubitsv3 import *
from Helper_Functions.instrument_helperfunctions import *
from datetime import datetime
import pyvisa as visa
import time
import scipy as sp
from typing import Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)
info = logger.info
warning = logger.warning
error = logger.error


_default_selected_ro_lines = [
    1,
    2,
    3,
    4,
    5,
    6
]
_default_vna_ip = "192.168.0.27"


class RoundTripGain:
    def __init__(
            self,
            qubits = _default_selected_ro_lines,
            rr_freq_overrides = None,
            sys_config = None,
            freq_range = [4,9], #GHz,
            vna_rf_power = -30, #dBm
            vna_ip = _default_vna_ip,
            avgs = 40,
            avg_wait = 10, #wait time in seconds

            ):

        self.rm = visa.ResourceManager()
        self.freq_axis = None
        self.kna = None
        self.avgs = avgs
        self.avg_wait = avg_wait
        self.gain_lines = qubits
        self.qubits = qubits
        self.freq_range = freq_range
        self.vna_rf_power = vna_rf_power
        self.vna_scpi_addr = f"TCPIP0::{vna_ip}::inst0::INSTR"


        self.readout_frequencies = [self._get_rr_settings(qubit)['rr_freq'] for qubit in self.qubits]

        self.rr_lo_settings = [self._get_rr_settings(qubit)['rr_lo'] for qubit in self.qubits]
        check_USB_switch_status()
        self.set_up_vna_for_round_trip_gain()

        self.gain_profile = {f"{i}": None for i in self.gain_lines}



    def _get_rr_settings(self, rr_line: int = 1) -> Dict:
        """gives the rr_settings as a dictionary output after loading the cfg dicts """
        result_dict = {
            'rr_lo': rr_LO[rr_line],
            'rr_freq': rr_LO[rr_line] + rr_IF[rr_line]
        }
        return result_dict

    def set_up_vna_for_round_trip_gain(self):
        info(f"setting up vna at {self.vna_scpi_addr}")
        rm = visa.ResourceManager()
        self.rm = rm
        self.kna = rm.open_resource(self.vna_scpi_addr)
        self.kna.write(f":SOUR1:POW {self.vna_rf_power}")
        self.kna.write(":CALC1:FORM MLOG")
        self.kna.write(f":SENS1:FREQ:STAR {self.freq_range[0]}E9")
        self.kna.write(f":SENS1:FREQ:STOP {self.freq_range[1]}E9")
        self.kna.write(":SENS1:AVER ON")
        self.kna.write(f":SENS1:AVER:COUN {self.avgs}")


    def find_top_n_dips(freq_array, power_dbm, fmin=5e9, fmax=8e9, N=5,
                        prominence=1.0, distance=50):

        # 1. Window the data
        mask = (freq_array >= fmin) & (freq_array <= fmax)
        f_win = freq_array[mask]
        p_win = power_dbm[mask]

        # 2. Find dips by finding peaks in inverted signal
        inv_signal = -p_win
        peaks, props = find_peaks(
            inv_signal,
            prominence=prominence,
            distance=distance
        )

        if len(peaks) == 0:
            return []

        # 3. Sort dips by depth (deepest first)
        peak_prom = props["prominences"]
        order = np.argsort(peak_prom)[::-1]

        peaks = peaks[order][:N]
        peak_prom = peak_prom[order][:N]

        # 4. Package results
        dips = []
        for idx, prom in zip(peaks, peak_prom):
            dips.append({
                "freq": f_win[idx],
                "power": p_win[idx],
                "prominence": prom
            })

        return dips

    def run_exp(self):
        self.freq_axis = np.array(
            self.kna.query_ascii_values("CALC1:MEAS1:X:VAL?")
        )
        for gain_line in self.gain_lines:
            switch_to_vna(keyer(f"q{gain_line}", dac_mapping))
            self.kna.write(f"SENS1:AVER:CLE")
            info(f"Waiting for avgs ({self.avg_wait}s")
            time.sleep(self.avg_wait)

            self.gain_profile[f"{gain_line}"]=np.array(self.kna.query_ascii_values("CALC1:MEAS1:DATA:FDAT?"))

        return self.gain_profile



    def analyse_data(self):
        for gain_line in self.gain_lines:
            dips_data = self.find_top_n_dips(
                freq_array=self.freq_axis,
                power_dbm=self.gain_profile[f"{gain_line}"],
            )


























