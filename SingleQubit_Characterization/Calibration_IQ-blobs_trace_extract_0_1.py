from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
# matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from qualang_tools.analysis.discriminator import two_state_discriminator
from Helper_Functions.macros import *
import scipy as sp
import os
from datetime import datetime

save_data = False # doesn't work as expected
rescale = False
update_pars = False
pi12 = False
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
q_no = 1
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]
nshots = 5e4

rep_rate_clk = 250000
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
ro_len = ro_len_clk[str(q_no)]

time_factor = 960 / (integ_len_clk[f"{q_no}"] * 4)

config["integration_weights"][f"new_dummy_cos{q_no}"] = {}
config["integration_weights"][f"new_dummy_minusSin{q_no}"] = {}

config["integration_weights"][f"new_dummy_cos{q_no}"]["cosine"] = [
    (np.cos(optimal_readout_phase[f"rr{q_no}"]), int(integ_len_clk[f"{q_no}"] * 4 * time_factor)),
    (0, integ_len_clk[f"{q_no}"] * 4 - int(integ_len_clk[f"{q_no}"] * 4 * time_factor))]

config["integration_weights"][f"new_dummy_cos{q_no}"]["sine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(integ_len_clk[f"{q_no}"] * 4 * time_factor)),
    (0, integ_len_clk[f"{q_no}"] * 4 - int(integ_len_clk[f"{q_no}"] * 4 * time_factor))]

config["integration_weights"][f"new_dummy_minusSin{q_no}"]["cosine"] = [
    (-np.sin(optimal_readout_phase[f"rr{q_no}"]), int(integ_len_clk[f"{q_no}"] * 4 * time_factor)),
    (0, integ_len_clk[f"{q_no}"] * 4 - int(integ_len_clk[f"{q_no}"] * 4 * time_factor))]

config["integration_weights"][f"new_dummy_minusSin{q_no}"]["sine"] = [
    (-np.cos(optimal_readout_phase[f"rr{q_no}"]), int(integ_len_clk[f"{q_no}"] * 4 * time_factor)),
    (0, integ_len_clk[f"{q_no}"] * 4 - int(integ_len_clk[f"{q_no}"] * 4 * time_factor))]

config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_cos'] = f"new_dummy_cos{q_no}"
config["pulses"][f"q{q_no}_ro_pulse"]["integration_weights"]['new_dummy_minusSin'] = f"new_dummy_minusSin{q_no}"

demod_weight_flg = 1

###################
# The QUA program #
###################

dem = 3.123e-05
a_rr = 1.0
with program() as IQ_blobs:
    n = declare(int)
    I = declare(fixed)
    Q = declare(fixed)
    I0 = declare(fixed)
    I0_st = declare_stream(adc_trace=True)
    Q0 = declare(fixed)
    Q0_st = declare_stream(adc_trace=True)
    I1 = declare(fixed)
    I1_st = declare_stream(adc_trace=True)
    Q1 = declare(fixed)
    Q1_st = declare_stream(adc_trace=True)
    adc_st_0 = declare_stream(adc_trace=True)
    adc_st_1 = declare_stream(adc_trace=True)

    with for_(n, 0, n < nshots, n + 1):
        cooldown(time=rep_rate_clk)

        # wait(rep_rate_clk, qe)
        reset_phase(rr)
        play("I", qe)
        align(qe, qe_12)
        play('X180', qe_12)
        align(qe_12, rr)
        # wait(wait_rr, rr)
        if demod_weight_flg:
            measure("readout" * amp(a_rr), rr, adc_st_0)
        else:
            measure("readout" * amp(a_rr), rr, adc_st_0)
        # save(I0, I0_st)
        # save(Q0, Q0_st)

        align()
        cooldown(time=rep_rate_clk)
        # wait(rep_rate_clk, qe)
        play_X180(qe)
        align(qe, qe_12)
        play('X180', qe_12)
        align(qe_12, rr)
        # align(qe, rr)
        wait(wait_rr, rr)
        if demod_weight_flg:
            measure("readout" * amp(a_rr), rr, adc_st_1)
        else:
            measure("readout" * amp(a_rr), rr, adc_st_1)
        # save(I1, I1_st)
        # save(Q1, Q1_st)

    with stream_processing():
        # I0_st.save_all('I0')
        # Q0_st.save_all('Q0')
        # I1_st.save_all('I1')
        # Q1_st.save_all('Q1')
        if int(out[-1]) % 2 == 1:
            adc_st_1.input1().save_all("adc_1_raw")
            adc_st_0.input1().save_all("adc_0_raw")
            adc_st_1.input1().average().save("adc_1")
            adc_st_0.input1().average().save("adc_0")
        else:
            adc_st_1.input2().save_all("adc_1_raw")
            adc_st_0.input2().save_all("adc_0_raw")
            adc_st_1.input2().average().save("adc_1")
            adc_st_0.input2().average().save("adc_0")

qm = qmm.open_qm(config)
job = qm.execute(IQ_blobs)

# I0_handle = job.result_handles.get("I0")
# Q0_handle = job.result_handles.get("Q0")
# I1_handle = job.result_handles.get("I1")
# Q1_handle = job.result_handles.get("Q1")
adc_1_handle = job.result_handles.get("adc_1")
adc_0_handle = job.result_handles.get("adc_0")
adc_1_raw_handle = job.result_handles.get("adc_1_raw")
adc_0_raw_handle = job.result_handles.get("adc_0_raw")
job.result_handles.wait_for_all_values()

# I0 = I0_handle.fetch_all()["value"]
# Q0 = Q0_handle.fetch_all()["value"]
# I1 = I1_handle.fetch_all()["value"]
# Q1 = Q1_handle.fetch_all()["value"]
adc_1 = adc_1_handle.fetch_all()
adc_0 = adc_0_handle.fetch_all()
adc_1_raw = adc_1_raw_handle.fetch_all()["value"]
adc_0_raw = adc_0_raw_handle.fetch_all()["value"]

# Plot averaged traces
plt.figure()
plt.plot(adc_1, label='adc_1 (averaged)')
plt.plot(adc_0, label='adc_0 (averaged)')
plt.title('Averaged ADC Traces')
plt.legend()
plt.grid()
plt.show(block=False)

# Plot raw (single-shot) traces - show first 10 traces as examples
plt.figure()
num_traces_to_show = min(10, len(adc_1_raw))
for i in range(num_traces_to_show):
    plt.plot(adc_1_raw[i], alpha=0.3, color='red', linewidth=0.5)
    plt.plot(adc_0_raw[i], alpha=0.3, color='blue', linewidth=0.5)
plt.plot(adc_1, label='adc_1 (averaged)', color='darkred', linewidth=2)
plt.plot(adc_0, label='adc_0 (averaged)', color='darkblue', linewidth=2)
plt.title(f'Raw ADC Traces (showing first {num_traces_to_show} shots)')
plt.legend()
plt.grid()
plt.show(block=False)

op_phase = optimal_readout_phase[rr]

# Save raw ADC traces
print("Preparing raw ADC traces for saving...")
num_shots = len(adc_0_raw)
adc_trace_length = len(adc_0_raw[0]) if num_shots > 0 else len(adc_0)

# Create array with shape (state0/1, IQ, shots, trace_length)
# state 0 = ground state, state 1 = excited state
# IQ: 0 = raw ADC signal (since raw ADC is one signal, not separate I/Q)
# For raw traces, IQ dimension is size 1
raw_traces_data = np.zeros((2, 1, num_shots, adc_trace_length))

# Store raw ADC traces
raw_traces_data[0, 0, :, :] = np.array(adc_0_raw)  # State 0, all shots, full trace
raw_traces_data[1, 0, :, :] = np.array(adc_1_raw)  # State 1, all shots, full trace

# Save to numpy file in the same directory as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
save_dir = script_dir

now = datetime.now()
timestamp = now.strftime("%Y%m%d_%H%M%S")
filename = f"raw_ADC_traces_q{q_no}_{timestamp}.npy"
filepath = os.path.join(save_dir, filename)

np.save(filepath, raw_traces_data)
print(f"\n{'='*60}")
print(f"Raw ADC traces saved successfully!")
print(f"File path: {filepath}")
print(f"Array shape: {raw_traces_data.shape}")
print(f"  - Dimension 0: State (0=ground, 1=excited)")
print(f"  - Dimension 1: IQ channel (0=raw ADC signal)")
print(f"  - Dimension 2: Shot number ({num_shots} shots)")
print(f"  - Dimension 3: Trace length ({adc_trace_length} samples per trace)")
print(f"{'='*60}\n")
#
# if rescale:
#     I0 = 1e6 * I0 / ro_len
#     Q0 = 1e6 * Q0 / ro_len
#     I1 = 1e6 * I1 / ro_len
#     Q1 = 1e6 * Q1 / ro_len
#
# angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1, b_print=True, b_plot=True)
# print(f"Ig, Ie = {np.mean(I0)}, {np.mean(I1)}")
# print(f"Qg, Qe = {np.mean(Q0)}, {np.mean(Q1)}")
#
i = len(adc_1) // 3
e = 2 * len(adc_1) // 3
#
Y_1 = np.fft.fft(adc_1[i:e]) * (2 / len(adc_1[i:e]))
Y_0 = np.fft.fft(adc_0[i:e]) * (2 / len(adc_0[i:e]))
#
X = np.fft.fftfreq(n=len(adc_1[i:e]), d=1e-9)
#
Y_1 = Y_1[1:len(Y_1) // 2]
Y_0 = Y_0[1:len(Y_0) // 2]
X = X[1:len(X) // 2]
#
# a = np.where(np.abs(Y_1) == np.max(np.abs(Y_1)))[0][0]
# b = np.where(np.abs(Y_0) == np.max(np.abs(Y_0)))[0][0]
#
# max_amp_1 = np.abs(Y_1)[a]
# max_amp_2 = np.abs(Y_0)[b]
#
# plt.figure()
# plt.plot(X, np.abs(Y_1), label='1 fft')
# plt.plot(X, np.abs(Y_0), label='0 fft')
# plt.legend()
# plt.grid()
#
t = np.linspace(0, len(adc_1), len(adc_1) + 1)
t = t * 1e-9
demod_carr_sin = np.sin(2 * np.pi * rr_IF[f'{q_no}'] * 1 * t[:-1] - op_phase)
demod_carr_cos = np.cos(2 * np.pi * rr_IF[f'{q_no}'] * 1 * t[:-1] - op_phase)
#
demod_0_cos = adc_0 * demod_carr_cos * (np.cos(optimal_readout_phase[f"rr{q_no}"]*1.1))
demod_0_sin = adc_0 * demod_carr_sin * (-np.sin(optimal_readout_phase[f"rr{q_no}"]*1.1))
demod_1_cos = adc_1 * demod_carr_cos * (np.cos(optimal_readout_phase[f"rr{q_no}"]*1.1))
demod_1_sin = adc_1 * demod_carr_sin * (-np.sin(optimal_readout_phase[f"rr{q_no}"]*1.1))
#
# Integration weights should match the length of the ADC trace
adc_trace_length = len(adc_1)
integration_window = int(time_factor * integ_len_clk[f"{q_no}"] * 4)
# Ensure integration window doesn't exceed ADC trace length
integration_window = min(integration_window, adc_trace_length)
#
integ_weights_cos = np.ones(integration_window) * (np.cos(optimal_readout_phase[f"rr{q_no}"]*1.1))
integ_weights_sin = np.ones(integration_window) * (-np.sin(optimal_readout_phase[f"rr{q_no}"]*1.1))
#
# Padding to match ADC trace length
padding_window = adc_trace_length - integration_window
padding_weight = np.zeros(padding_window)
#
integ_weights_cos = np.append(integ_weights_cos, padding_weight)
integ_weights_sin = np.append(integ_weights_sin, padding_weight)
#
carr_part = np.multiply(demod_carr_cos, integ_weights_cos) + np.multiply(demod_carr_sin, integ_weights_sin)

adc_windowed_demod_full_I0 = np.dot(carr_part, adc_0)/(4096*4096)
adc_windowed_demod_full_I1 = np.dot(carr_part, adc_1)/(4096*4096)
#
#
#
#
sos = sp.signal.butter(10, 1e7, 'lp', output='sos', fs=1e9)
demod_flt_0_cos = sp.signal.sosfilt(sos, demod_0_cos)
demod_flt_1_cos = sp.signal.sosfilt(sos, demod_1_cos)
demod_flt_0_sin = sp.signal.sosfilt(sos, demod_0_sin)
demod_flt_1_sin = sp.signal.sosfilt(sos, demod_1_sin)
plt.figure()
plt.plot(demod_1_cos, label='Demod 1 cos')
plt.plot(demod_0_cos, label='Demod 0 cos')
plt.plot(demod_flt_1_cos[50:], label='Demod filtered 1 cos')
plt.plot(demod_flt_0_cos[50:], label='Demod filtered 0 cos')
plt.legend()
plt.grid()
plt.show(block=False)

plt.figure()
plt.plot(demod_1_sin, label='Demod 1 sin')
plt.plot(demod_0_sin, label='Demod 0 sin')
plt.plot(demod_flt_1_sin[50:], label='Demod filtered 1 sin')
plt.plot(demod_flt_0_sin[50:], label='Demod filtered 0 sin')
plt.legend()
plt.grid()
plt.show(block=False)
#
# plt.figure()
# plt.plot(adc_0, label = 'ADC 0')
# plt.plot(adc_1, label = 'ADC 1')
# # plt.plot(np.cumsum(adc_0), label='cumulative adc 0')
# # plt.plot(np.cumsum(adc_1), label='cumulative adc 1')
# plt.legend()
# plt.grid()
#
# # def filter_to_QUA_format(filter):
# #
# #     qua_formatted = []
# #     index = 1
# #
# #     for i in range(len(filter)):
#
#
#
# if save_data:
#     file_saver_(np.transpose([I0, Q0, I1, Q1]), file_name=__file__,
#                 master_folder=ExpName, header_string="I0, Q0, I1, Q1")
