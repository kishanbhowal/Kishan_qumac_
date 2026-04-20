import json
from Helper_Functions.macros import measure_macro, cooldown
from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
from Helper_Functions.analysis_functions import *
from Helper_Functions.macros import *
from qualang_tools.analysis.discriminator import two_state_discriminator
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from Helper_Functions.macros import measure_macro
from scipy.signal import butter, filtfilt, cheby1, cheby2
from scipy.signal import convolve

q_no = 3
qe = f"q{q_no}"
qe_12 = f"q12_{q_no}"
rr = f"rr{q_no}"
ro_len = ro_len_clk[str(q_no)]
out = adc_mapping[rr]
pi_len_config = pi_len_ns[f"{q_no}"]

rr_I = dac_mapping[rr][1][0]
rr_Q = dac_mapping[rr][1][1]

avgs = 50
pi_12 = False
simulate = False
update_weights = True
con = f'con{dac_mapping[qe][0]}'

# --- Parameters ---
n_avg = 2000
wait_rr = 4
readout_len = 4*ro_len_clk[f'{q_no}']
IF_freq = copy.copy(rr_IF[f'{q_no}'])
dem = 3.123e-05
single = False
rescale = True
chunk_size = 2
num_slices = int(readout_len / (chunk_size * 4))

if simulate:
    rep_rate_clk = 3000
else:
    rep_rate_clk = 250000

qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)

# Helper function for digital low-pass filtering
def lowpass_filter(data, cutoff_freq, sample_rate=1e9, order=4, ripple_db=0.1, stopband_attenuation_db=40):
    nyq = 0.5 * sample_rate
    normal_cutoff = cutoff_freq / nyq
    # b, a = butter(4, normal_cutoff, btype='low', analog=False)
    b, a = cheby1(order, ripple_db, normal_cutoff, btype='low', analog=False)
    # b, a = cheby2(order, stopband_attenuation_db, normal_cutoff, btype='low', analog=False)
    # data1 = filtfilt(b, a, data)
    # data2 = filtfilt(b, a, data1)
    return filtfilt(b, a, data)


def create_optimal_weight_list(weights_array, chunk_size_ns):
    return [(float(np.real(w)), chunk_size_ns) for w in weights_array]


# --- 1. QUA Program to Acquire Raw ADC Traces ---
with program() as raw_trace_prog:
    n = declare(int)
    I = declare(fixed)
    Q = declare(fixed)
    I0 = declare(fixed)
    Q0 = declare(fixed)
    I1 = declare(fixed)
    Q1 = declare(fixed)

    # I_slice = declare(fixed)
    # Q_slice = declare(fixed)
    I_single_st = declare_stream()
    Q_single_st = declare_stream()
    Q1_st = declare_stream()
    I1_st = declare_stream()
    Q0_st = declare_stream()
    I0_st = declare_stream()
    I_st_0 = declare_stream()
    Q_st_0 = declare_stream()
    I_st_1 = declare_stream()
    Q_st_1 = declare_stream()

    # Declare streams to capture the raw 1GSPS ADC data
    adc_st_0 = declare_stream(adc_trace=True)
    adc_st_2 = declare_stream(adc_trace=True)

    I_slice = declare(fixed, size=int(num_slices))
    Q_slice = declare(fixed, size=int(num_slices))

    m = declare(int)

    with for_(n, 0, n < n_avg, n + 1):

        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=pi_12, dem=dem)
        reset_frame(qe, rr)
        # reset_phase(rr)
        play("I", qe)
        align(qe, qe_12, rr)

        # measure_macro(qe, rr, out, I0, Q0, pi_12=pi_12)

        # Measure and send raw ADC data to stream
        # measure("readout", rr, adc_st_0)
        if single:
            measure_macro(qe, rr, out, I0, Q0, pi_12=False)
            save(I0, I0_st)
            save(Q0, Q0_st)
        else:
            # measure("readout", rr, adc_st_0)
            measure("readout", rr, None,
                    demod.sliced("integW_cos", I_slice, chunk_size, out),
                    demod.sliced("integW_sin", Q_slice, chunk_size, out))
            # save(I_slice, I_st_0)
            # save(Q_slice, Q_st_0)
            # m = declare(int)
            with for_(m, 0, m < num_slices, m + 1):
                save(I_slice[m], I_st_0)
                save(Q_slice[m], Q_st_0)

        align()


        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=pi_12, dem=dem)
        # # -- Measure |2> State --
        reset_frame(qe, rr)
        play_X180(qe)

        if pi_12:
            # wait(wait_time, qe)  # Wait for thermal relaxation
            align(qe, qe_12)
            wait(4, qe_12)
            play('X180', qe_12)  # Your pi_12 pulse
            #
            # # Your specific readout timing alignment
            wait(wait_rr, rr)
            align(qe_12, rr)
            wait(wait_rr, rr)
        else:
            align(qe, qe_12, rr)
            wait(wait_rr, rr)
        #
        # # Measure and send raw ADC data to stream
        # measure("readout", rr, adc_st_2)
        # measure_macro(qe, rr, out, I1, Q1, pi_12=False)
        if single:
            measure_macro(qe, rr, out, I1, Q1, pi_12=False)
            save(I1, I1_st)
            save(Q1, Q1_st)
        else:
            # measure("readout", rr, adc_st_2)
            measure("readout", rr, None,
                    demod.sliced("integW_cos", I_slice, chunk_size, out),
                    demod.sliced("integW_sin", Q_slice, chunk_size, out))
            # save(I_slice, I_st_1)
            # save(Q_slice, Q_st_1)

            with for_(m, 0, m < num_slices, m + 1):
                save(I_slice[m], I_st_1)
                save(Q_slice[m], Q_st_1)


    with stream_processing():
        # The OPX typically has two analog inputs (I and Q)
        if single:
            I0_st.save_all('I0')
            Q0_st.save_all('Q0')
            I1_st.save_all('I1')
            Q1_st.save_all('Q1')

        else:
            # if q_no%2 == 0:
            #     adc_st_0.buffer(n_avg).save('I_0_raw')
            #     adc_st_2.buffer(n_avg).save('I_2_raw')
            # else:
            #     adc_st_0.input1().buffer(n_avg).save('I_0_raw')
            #     adc_st_2.input1().buffer(n_avg).save('I_2_raw')

            I_st_0.buffer(num_slices).average().save('I_0_sliced')
            Q_st_0.buffer(num_slices).average().save('Q_0_sliced')
            I_st_1.buffer(num_slices).average().save('I_1_sliced')
            Q_st_1.buffer(num_slices).average().save('Q_1_sliced')


if simulate:
    job = qmm.simulate(config, raw_trace_prog, SimulationConfig(int(20000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    # samples.con1.plot()
    samples.con1.plot()
    plt.show(block=False)

    raise Halted()

# --- 2. Execute and Fetch Data ---
# qmm = QuantumMachinesManager(host, port)
qm = qmm.open_qm(config)
job = qm.execute(raw_trace_prog)
job.result_handles.wait_for_all_values()



if single:

    I0_handle = job.result_handles.get("I0")
    Q0_handle = job.result_handles.get("Q0")
    I1_handle = job.result_handles.get("I1")
    Q1_handle = job.result_handles.get("Q1")
    job.result_handles.wait_for_all_values()

    I0 = I0_handle.fetch_all()["value"]
    Q0 = Q0_handle.fetch_all()["value"]
    I1 = I1_handle.fetch_all()["value"]
    Q1 = Q1_handle.fetch_all()["value"]

    if rescale:
        I0 = 1e6 * I0 / ro_len
        Q0 = 1e6 * Q0 / ro_len
        I1 = 1e6 * I1 / ro_len
        Q1 = 1e6 * Q1 / ro_len

    angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1, b_print=True, b_plot=True)
    plt.show(block=False)
    print(f"Ig, Ie = {np.mean(I0)}, {np.mean(I1)}")
    print(f"Qg, Qe = {np.mean(Q0)}, {np.mean(Q1)}")


else:

     # Fetch the raw data arrays
    I_0 = job.result_handles.get('I_0_sliced').fetch_all()
    Q_0 = job.result_handles.get('Q_0_sliced').fetch_all()
    I_1 = job.result_handles.get('I_1_sliced').fetch_all()
    Q_1 = job.result_handles.get('Q_1_sliced').fetch_all()

    # Reconstruct the complex baseband signals
    baseband_0 = I_0 + 1j * Q_0
    baseband_1 = I_1 + 1j * Q_1

    # Calculate the difference and format the weights
    diff_sig = baseband_1 - baseband_0
    diff_sig = baseband_0
    w_opt = np.conj(diff_sig)

    # Normalize and plot
    w_opt = w_opt / np.linalg.norm(w_opt)



    flat_end_idx = 12


 # 2. Define your 'Integration Cutoff'
 # Find the index where the signal starts to 'fall'
 # If your flat region ends at slice 15, we want to taper after that.


 # 3. Apply the T1 'Penalty'
 # We don't touch the rise or the flat part,
 # but we exponentially kill the weights during the 'fall'.
    t_axis = np.arange(len(w_opt)) * chunk_size * 4  # 40ns per slice
    T1_const = 1200  # Your qubit T1 in ns

 # Taper only the section where decay is likely to dominate
    decay_taper = np.ones(len(w_opt))
    decay_taper[flat_end_idx:] = np.exp(-(t_axis[flat_end_idx:] - t_axis[flat_end_idx]) / T1_const)

    w_opt_protected = w_opt * decay_taper

 # 4. Final Normalization
    w_opt_protected /= np.max(np.abs(w_opt_protected))
    # w_opt_protected /= np.linalg.norm(w_opt)

    plt.figure()
    plt.plot(np.real(w_opt_protected), label='I Weight')
    plt.plot(np.imag(w_opt_protected), label='Q Weight')
    plt.title("Hardware-Demodulated Optimal Weights")
    plt.legend()
    plt.show(block=False)

#     t_1ns = np.arange(readout_len) * 1e-9
#
#     # Demodulate a REAL signal into a COMPLEX baseband
#     # Multiply by 2 to recover the amplitude lost to the negative frequency component
#     demod_0 = 2 * I_0 * np.exp(-1j * 2 * np.pi * IF_freq * t_1ns)
#     demod_2 = 2 * I_2 * np.exp(-1j * 2 * np.pi * IF_freq * t_1ns)
#
#     # Dynamically set cutoff to half the IF
#     dynamic_cutoff = IF_freq*0.5
#     if np.abs(dynamic_cutoff) < 5e6:
#         dynamic_cutoff = 5e6
#
#     # Filter out the 2*omega_IF high-frequency mixing products
#     baseband_0 = np.array([lowpass_filter(data, cutoff_freq=np.abs(dynamic_cutoff)) for data in demod_0])
#     baseband_2 = np.array([lowpass_filter(data, cutoff_freq=np.abs(dynamic_cutoff)) for data in demod_2])
#
#     bb_0_avg = np.mean(baseband_0, axis=0)
#     bb_1_avg = np.mean(baseband_2, axis=0)
#
#     # The optimal complex trajectory is the difference
#     diff_sig = bb_1_avg - bb_0_avg
#
#     plt.figure()
#     plt.plot(np.real(bb_0_avg))
#     plt.plot(np.real(bb_1_avg))
#     plt.plot(np.real(diff_sig))
#     plt.show(block=False)
#
#     # diff_sig = np.flip(diff_sig)
#
#     # --- 4. Format for OPX Hardware (Downsample and Normalize) ---
#     # The OPX updates integration weights every 4ns clock cycle.
#     # We reshape the 1ns array into chunks of 4 and average them.
#     diff_4ns = np.mean(diff_sig.reshape(-1, 4), axis=1)
#
#     # Separate into I and Q weights
#     W_I = np.real(diff_4ns)
#     W_Q = np.imag(diff_4ns)
#
#     # CRITICAL: FPGA fixed-point normalization.
#     # OPX weights must strictly fall in the range [-2.0, 1.999).
#     # If your weights are too large, the FPGA math will overflow and wrap around, destroying your measurement.
#     max_val = np.max(np.abs([W_I, W_Q]))
#     scale_factor = 1.9 / max_val if max_val > 0 else 1.0

    # w_opt_protected = np.flip(w_opt_protected)

    # W_I_normalized = np.real(w_opt)
    # W_Q_normalized = np.imag(w_opt)
    # wt_data = {q_no: weights_data}

    def create_inverse_filter(x, y, alpha=0.01):
         """
         x: Input signal (np.array)
         y: System response (np.array)
         alpha: Regularization parameter (higher = smoother/less noise, lower = sharper)
         """
         # 1. Transform to Frequency Domain
         X = np.fft.fft(x)
         Y = np.fft.fft(y)

         # 2. Estimate System Transfer Function H = Y / X
         # We add a tiny epsilon to X to avoid division by zero
         H = Y / (X + 1e-12)

         # 3. Create the Inverse Filter G using Tikhonov Regularization
         # G = H* / (|H|^2 + alpha^2)
         H_conj = np.conj(H)
         G = H_conj / (np.abs(H) ** 2 + alpha ** 2)

         # 4. Convert back to Time Domain
         inverse_filter = (np.fft.ifft(G))

         # 5. Shift the filter so the impulse is centered (optional but helpful)
         inverse_filter = np.fft.fftshift(inverse_filter)

         return inverse_filter

    readout_signal = [1]*len(baseband_0)

    iv_fltr_0 = create_inverse_filter(readout_signal, baseband_0, alpha=0.1)
    iv_fltr_1 = create_inverse_filter(readout_signal, baseband_1, alpha=0.1)

    iv_fltr_0 /= np.max(np.abs(iv_fltr_0))
    iv_fltr_1 /= np.max(np.abs(iv_fltr_1))

    iv_mean = 0.5*(iv_fltr_1+iv_fltr_0)

    # w_opt = np.roll(w_opt,-5)

    opt_weights_real = create_optimal_weight_list(w_opt_protected, chunk_size * 4)  # 40ns per slice
    opt_weights_minus_imag = create_optimal_weight_list(-w_opt_protected * 1j, chunk_size * 4)  # For complex demod

     #     # W_I_normalized = np.array([np.cos(optimal_readout_phase[rr]*(np.pi/180))]*len(W_I_normalized))
     #     # W_Q_normalized = np.array([-1*np.sin(optimal_readout_phase[rr]*(np.pi/180))]*len(W_Q_normalized))
     #
     #     # These lists go directly into your QM configuration dictionary
     #     print("Optimal cosine weights (W_I):", W_I_normalized.tolist())
     #     print("Optimal sine weights (W_Q):", W_Q_normalized.tolist())
     #
     #     # Create a dictionary to hold the weights for this specific resonator
    weights_data = {
         "optW_cos": opt_weights_real,
         "optW_minus_sin": opt_weights_minus_imag
    }

# Recover the original signal
    # x_recovered = convolve(baseband_0, iv_fltr_0, mode='same')

    if update_weights:
        # Define a clean filename, e.g., optimal_weights_rr6.json
        filename = f"../Configuration_Files/Readout_Settings/optimal_weights.json"

        with open(filename, 'r') as f:
            wts_data = json.load(f)

        # if q_no not in wts_data.keys():
        #     wts_data[q_no] = {}

        wts_data[rr] = weights_data

        # Save to JSON
        with open(filename, "w") as f:
            json.dump(wts_data, f, indent=4)
