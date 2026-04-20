# This file contains classes of spectrum analyzers using the VISA interface to communicate with the computers.
# They should have almost uniform commands, making adaptions to new models/brands quite easy

from qm.qua import *
from abc import ABC, abstractmethod
import numpy as np
import pyvisa as visa


class VisaSA(ABC):
    def __init__(self, address, qm = None):
        # Gets an existing qm, assumes there is an element called "qubit" with an operation named "test_pulse" which
        # plays a constant pulse
        super().__init__()
        rm = visa.ResourceManager()
        self.sa = rm.open_resource(address)
        self.sa.timeout = 100000

        with program() as mixer_cal:
            with infinite_loop_():
                #play("test_pulse", "qubit")
                wait(100)

        # self.qm = qm
        # self.job = qm.execute(mixer_cal) ## Commented because of error after OPX+ update
        self.method = None

    def IQ_imbalance_correction(self, g, phi):
        c = np.cos(phi)
        s = np.sin(phi)
        N = 1 / ((1 - g**2) * (2 * c**2 - 1))
        return [float(N * x) for x in [(1 - g) * c, (1 + g) * s, (1 - g) * s, (1 + g) * c]]

    def get_leakage(self, i0, q0):
        self.qm.set_dc_offset_by_qe("qubit", "I", i0)
        self.qm.set_dc_offset_by_qe("qubit", "Q", q0)
        amp_ = self.get_amp()
        return amp_

    def get_image(self, g, p):
        self.job.set_element_correction("qubit", self.IQ_imbalance_correction(g, p))
        amp_ = self.get_amp()
        return amp_

    def __del__(self):
        self.sa.clear()
        self.sa.close()

    @abstractmethod
    def get_amp(self):
        pass

    @abstractmethod
    def set_automatic_video_bandwidth(self, state: int):
        # State should be 1 or 0
        pass

    @abstractmethod
    def set_automatic_bandwidth(self, state: int):
        # State should be 1 or 0
        pass

    @abstractmethod
    def set_bandwidth(self, bw: int):
        # Sets the bandwidth
        pass

    @abstractmethod
    def set_sweep_points(self, n_points: int):
        # Sets the number of points for a sweep
        pass

    @abstractmethod
    def set_center_freq(self, freq: int):
        # Sets the central frequency
        pass

    @abstractmethod
    def set_span(self, span: int):
        # Sets the span
        pass

    @abstractmethod
    def set_cont_off(self):
        # Sets continuous mode off
        pass

    @abstractmethod
    def set_cont_on(self):
        # Sets continuous mode on
        pass

    @abstractmethod
    def get_single_trigger(self):
        # Performs a single sweep
        pass

    @abstractmethod
    def active_marker(self, marker: int):
        # Active the given marker
        pass

    @abstractmethod
    def set_marker_freq(self, marker: int, freq: int):
        # Sets the marker's frequency
        pass

    @abstractmethod
    def query_marker(self, marker: int):
        # Query the marker
        pass

    @abstractmethod
    def get_full_trace(self):
        # Returns the full trace
        pass

    @abstractmethod
    def enable_measurement(self):
        # Sets the measurement to channel power
        pass

    @abstractmethod
    def disables_measurement(self):
        # Sets the measurement to none
        pass

    @abstractmethod
    def sets_measurement_integration_bw(self, ibw: int):
        # Sets the measurement integration bandwidth
        pass

    @abstractmethod
    def disables_measurement_averaging(self):
        # Disables averaging in the measurement
        pass

    @abstractmethod
    def get_measurement_data(self):
        # Returns the result of the measurement
        pass


class RohdeSchwarzFPC1000(VisaSA):
    def get_amp(self):
        self.get_single_trigger()
        if self.method == 1:  # Channel power
            sig = self.get_measurement_data()
        elif self.method == 2:  # Marker
            sig = self.query_marker(1)
        else:
            sig = float("NaN")
        return sig

    def set_automatic_video_bandwidth(self, state: int):
        # State should be 1 or 0
        self.sa.write(f"SENS:BAND:VID:AUTO {int(state)}")

    def set_automatic_bandwidth(self, state: int):
        # State should be 1 or 0. Resolution (or measurement) bandwidth
        self.sa.write(f"SENS:BAND:AUTO {int(state)}")

    def set_bandwidth(self, bw: int):
        # Sets the resolution (or measurement) bandwidth, 1 Hz to 3 MHz, default unit is Hz
        # Example SENS:BAND 100000
        self.sa.write(f"SENS:BAND {int(bw)}")

    def set_sweep_points(self, n_points: int):
        # Sets the number of points for a sweep, allowed range 101 to 2501, default is 201
        self.sa.write(f"SENS:SWE:POIN {int(n_points)}")

    def set_center_freq(self, freq: int):
        # Sets the central frequency, default unit is Hz
        self.sa.write(f"SENS:FREQ:CENT {int(freq)}")

    def set_span(self, span: int):
        # Sets the span, default unit is Hz
        self.sa.write(f"SENS:FREQ:SPAN {int(span)}")

    def set_cont_off(self):
        # This command selects the sweep mode (but does not start the measurement!)
        # OFF or 0 is a single sweep mode
        # *OPC? is to make sure there is no overlapping execution
        return self.sa.query("INIT:CONT OFF;*OPC?")

    def set_cont_on(self):
        # This command selects the sweep mode (but does not start the measurement!)
        # ON or 1 is a continuous sweep mode
        # *OPC? is to make sure there is no overlapping execution
        return self.sa.query("INIT:CONT ON;*OPC?")

    def get_single_trigger(self):
        # Initiates a new measurement sequence (starts the sweep)
        return self.sa.query("INIT:IMM;*OPC?")

    def active_marker(self, marker: int):
        # Activate the given marker
        self.sa.write(f"CALC:MARK{int(marker)} ON")

    def set_marker_freq(self, marker: int, freq: int):
        # Sets the marker's frequency. Default unit is Hz
        self.get_single_trigger()
        self.sa.write(f"CALC:MARK{int(marker)}:X {int(freq)}")

    def query_marker(self, marker: int):
        # Query the amplitude (default unit is dBm) of the marker
        return float(self.sa.query(f"CALC:MARK{int(marker)}:Y?"))

    def get_full_trace(self):
        # Returns the full trace. Implicit assumption that this is trace1 (there could be 1-4)
        self.sa.write("FORM ASC")  # data format needs to be in ASCII
        ff_SA_Trace_Data = self.sa.query("TRAC:DATA? TRACE1")
        # Data from the FPC comes out as a string of 1183 values separated by ',':
        # '-1.97854112E+01,-3.97854112E+01,-2.97454112E+01,-4.92543112E+01,-5.17254112E+01,-1.91254112E+01...\n'
        # The code below turns it into an a python list of floats
        # Use split to turn long string to an array of values
        ff_SA_Trace_Data_Array = ff_SA_Trace_Data.split(",")
        amp = [float(i) for i in ff_SA_Trace_Data_Array]
        return amp

    def enable_measurement(self):
        # Sets the measurement to channel power
        self.sa.write(
            "CALC:MARK:FUNC:POW:SEL CPOW; CALC:MARK:FUNC:LEV:ONCE; CALC:MARK:FUNC:CPOW:UNIT DBM; CALC:MARK:FUNC:POW:RES:PHZ ON"
        )

    def disables_measurement(self):
        # Sets the channel power measurement to none
        self.sa.write("CALC:MARK:FUNC:POW OFF")

    def sets_measurement_integration_bw(self, ibw: int):
        # Sets the measurement integration bandwidth for channel power measurements
        self.sa.write(f"CALC:MARK:FUNC:CPOW:BAND {int(ibw)}")

    def disables_measurement_averaging(self):
        # disables averaging in the measurement
        pass

    def get_measurement_data(self):
        # Returns the result of the measurement
        return self.sa.query(f"CALC:MARK:FUNC:POW:RES? CPOW")


class KeysightFieldFox(VisaSA):
    def get_amp(self):
        self.get_single_trigger()
        if self.method == 1:  # Channel power
            sig = self.get_measurement_data()
        elif self.method == 2:  # Marker
            sig = self.query_marker(1)
        else:
            sig = float("NaN")
        return sig

    def set_automatic_video_bandwidth(self, state: int):
        # State should be 1 or 0
        self.sa.write(f"SENS:BAND:VID:AUTO {int(state)}")

    def set_automatic_bandwidth(self, state: int):
        # State should be 1 or 0
        self.sa.write(f"SENS:BAND:AUTO {int(state)}")

    def set_bandwidth(self, bw: int):
        # Sets the bandwidth
        self.sa.write(f"SENS:BAND {int(bw)}")

    def set_sweep_points(self, n_points: int):
        # Sets the number of points for a sweep
        self.sa.write(f"SENS:SWE:POIN {int(n_points)}")

    def set_center_freq(self, freq: int):
        # Sets the central frequency
        self.sa.write(f"SENS:FREQ:CENT {int(freq)}")

    def set_span(self, span: int):
        # Sets the span
        self.sa.write(f"SENS:FREQ:SPAN {int(span)}")

    def set_cont_off(self):
        return self.sa.query("INIT:CONT OFF;*OPC?")

    def set_cont_on(self):
        # Sets continuous mode on
        return self.sa.query("INIT:CONT ON;*OPC?")

    def get_single_trigger(self):
        # Performs a single sweep
        return self.sa.query("INIT:IMM;*OPC?")

    def active_marker(self, marker: int):
        # Active the given marker
        self.sa.write(f"CALC:MARK{int(marker)}:ACT")

    def set_marker_freq(self, marker: int, freq: int):
        # Sets the marker's frequency
        self.get_single_trigger()
        self.sa.write(f"CALC:MARK{int(marker)}:X {int(freq)}")

    def query_marker(self, marker: int):
        # Query the marker
        return float(self.sa.query(f"CALC:MARK{int(marker)}:Y?"))

    def get_full_trace(self):
        # Returns the full trace
        ff_SA_Trace_Data = self.sa.query("TRACE:DATA?")
        # Data from the Fieldfox comes out as a string separated by ',':
        # '-1.97854112E+01,-3.97854112E+01,-2.97454112E+01,-4.92543112E+01,-5.17254112E+01,-1.91254112E+01...\n'
        # The code below turns it into an a python list of floats

        # Use split to turn long string to an array of values
        ff_SA_Trace_Data_Array = ff_SA_Trace_Data.split(",")
        amp = [float(i) for i in ff_SA_Trace_Data_Array]
        return amp

    def enable_measurement(self):
        # Sets the measurement to channel power
        self.sa.write("SENS:MEAS:CHAN CHP")

    def disables_measurement(self):
        # Sets the measurement to none
        self.sa.write("SENS:MEAS:CHAN NONE")

    def sets_measurement_integration_bw(self, ibw: int):
        # Sets the measurement integration bandwidth
        self.sa.write(f"SENS:CME:IBW {int(ibw)}")

    def disables_measurement_averaging(self):
        # disables averaging in the measurement
        self.sa.write("SENS:CME:AVER:ENAB 0")

    def get_measurement_data(self):
        # Returns the result of the measurement
        return float(self.sa.query("CALC:MEAS:DATA?").split(",")[0])
        # Data from the Fieldfox comes out as a string separated by ',':
        # '-1.97854112E+01,-3.97854112E+01\n'
        # The code above takes the first value and converts to float.


class KeysightXSeries(VisaSA):
    def q(self, cmd):
        return self.sa.query(cmd).strip()

    def query(self, cmd):
        return self.q(cmd=cmd)

    def get_amp(self):
        self.get_single_trigger()
        if self.method == 1:  # Channel power
            sig = self.get_measurement_data()
        elif self.method == 2:  # Marker
            sig = self.query_marker(1)
        else:
            sig = float("NaN")
        return sig

    def set_automatic_video_bandwidth(self, state: int):
        # State should be 1 or 0
        self.sa.write(f"SENS:BAND:VID:AUTO {int(state)}")

    def set_automatic_bandwidth(self, state: int):
        # State should be 1 or 0
        self.sa.write(f"SENS:BAND:AUTO {int(state)}")

    def set_bandwidth(self, bw: int):
        # Sets the bandwidth
        self.sa.write(f"SENS:BAND {int(bw)}")

    def set_sweep_points(self, n_points: int):
        # Sets the number of points for a sweep
        self.sa.write(f"SENS:SWE:POIN {int(n_points)}")

    def set_center_freq(self, freq: int):
        # Sets the central frequency
        self.sa.write(f"SENS:FREQ:CENT {int(freq)}")

    def set_span(self, span: int):
        # Sets the span
        self.sa.write(f"SENS:FREQ:SPAN {int(span)}")

    def set_cont_off(self):
        return self.sa.query("INIT:CONT OFF;*OPC?")

    def set_cont_on(self):
        # Sets continuous mode on
        return self.sa.query("INIT:CONT ON;*OPC?")

    def get_single_trigger(self):
        # Performs a single sweep
        return self.sa.query("INIT:IMM;*OPC?")

    def active_marker(self, marker: int):
        # Active the given marker
        self.sa.write(f"CALC:MARK{int(marker)}:MODE POS")

    def set_marker_freq(self, marker: int, freq: int):
        # Sets the marker's frequency
        self.get_single_trigger()
        self.sa.write(f"CALC:MARK{int(marker)}:X {int(freq)}")

    def query_marker(self, marker: int):
        # Query the marker
        return float(self.sa.query(f"CALC:MARK{int(marker)}:Y?"))

    def get_full_trace(self):
        # Returns the full trace
        ff_SA_Trace_Data = self.sa.query("TRACE:DATA? TRACE1")
        # Data from the Keysight comes out as a string separated by ',':
        # '-1.97854112E+01,-3.97854112E+01,-2.97454112E+01,-4.92543112E+01,-5.17254112E+01,-1.91254112E+01...\n'
        # The code below turns it into an a python list of floats

        # Use split to turn long string to an array of values
        ff_SA_Trace_Data_Array = ff_SA_Trace_Data.split(",")
        amp = [float(i) for i in ff_SA_Trace_Data_Array]
        return amp

    def enable_measurement(self):
        # Sets the measurement to channel power
        self.sa.write(":CONF:CHP")

    def disables_measurement(self):
        # Sets the measurement to none
        self.sa.write(":CONF:CHP NONE")

    def sets_measurement_integration_bw(self, ibw: int):
        # Sets the measurement integration bandwidth
        self.sa.write(f"SENS:CHP:BAND:INT {int(ibw)}")

    def disables_measurement_averaging(self):
        # disables averaging in the measurement
        self.sa.write("SENS:CHP:AVER 0")

    def get_measurement_data(self):
        # Returns the result of the measurement
        return float(self.sa.query("READ:CHP?").split(",")[0])
        # Data from the Keysight comes out as a string separated by ',':
        # '-1.97854112E+01,-3.97854112E+01\n'
        # The code above takes the first value and converts to float.
    def get_freq_axis(self):
        f_center = float(self.sa.query("FREQ:CENT?"))
        f_span = float(self.sa.query("FREQ:SPAN?"))
        npts = int(self.sa.query("SWE:POIN?"))

        freq_axis = np.linspace(f_center - f_span / 2, f_center + f_span / 2, npts)
        return freq_axis

    def get_markers(self):
        markers = {
            "n": [],
            "mode": [],
            "trace": [],
            "x": [],
            "y": [],
        }

        for n in range(1, 13): #BUG: for n more than 13 we get a query unterminated error
            try:
                state = int(float(self.q(f":CALC:MARK{n}:STAT?")))
            except Exception as e:
                print("breaking", e)
                break

            if state == 1:
                trace = self.q(f":CALC:MARK{n}:TRAC?")
                x = float(self.q(f":CALC:MARK{n}:X?"))
                y = float(self.q(f":CALC:MARK{n}:Y?"))
                mode = self.q(f":CALC:MARK{n}:MODE?")
                markers["n"].append(n)
                markers["mode"].append(mode)
                markers["trace"].append(trace)
                markers["x"].append(x)
                markers["y"].append(y)

        return markers

    def get_detailed_trace(self, verbose = False):
        y_data = self.get_full_trace()
        freq_axis = self.get_freq_axis()
        marker_info = self.get_markers()
        if verbose:
            ref_level = self.q(":DISP:WIND:TRAC:Y:RLEV?")
            rbw = float(self.sa.query(":SENS:BAND:RES?").strip())
            rbw_auto = int(float(self.sa.query(":SENS:BAND:RES:AUTO?").strip()))
        else:
            ref_level, rbw, rbw_auto = None, None, None
        res = {
            "y_data": y_data,
            'freq_axis': freq_axis,
            'marker_info':marker_info,
            'ref_level' : ref_level,
            "rbw": rbw,
            "rbw_auto": rbw_auto
        }

        return res