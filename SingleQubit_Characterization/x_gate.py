import numpy as np
import time
from qm.qua import *
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
from qualang_tools.results import progress_counter, fetching_tool
import pyvisa as visa
from scipy import signal as sgn
from qualang_tools.plot import interrupt_on_close
from scipy.signal import find_peaks
import statistics as st
import matplotlib
from Helper_Functions.spectro_helper import *
from Helper_Functions.macros import cooldown, measure_macro
import sys
import pyvisa as visa
import json
simulate = False
save_data = False

qe = 2

