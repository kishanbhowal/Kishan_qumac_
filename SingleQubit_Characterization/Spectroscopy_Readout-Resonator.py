from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
# from configuration_octave import *
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

###################
# The QUA program #
###################

save_data = True
simulate = False
check_e_delay = False

rr_no = 4
rr = f"rr{rr_no}"
out = adc_mapping[rr]
ro_len = ro_len_clk[str(rr_no)]
# rep_rate_clk = 2500
# rr_LO = config["elements"][rr]["mixInputs"]["lo_frequency"]
rr_LO_val = rr_LO[f"{rr_no}"]
f_min = 10e6
f_max = 30e6
df = 0.025e6

# f_min = rr_LO_val-100e6
# f_max = rr_LO_val+100e6
# df = 10e6

if simulate:
    rep_rate_clk = 100
else:
    rep_rate_clk = 2500


if check_e_delay:
    f_min = -250e6
    f_max = 250e6
    df = 1e6

freq_list = np.arange(f_min, f_max, df)
zeros = np.where(freq_list == 0)[0]
if len(zeros):
    zero_i = zeros[0]

with program() as rr_spec:
    n = declare(int)
    I = declare(fixed)
    I_st = declare_stream()
    Q = declare(fixed)
    Q_st = declare_stream()
    f = declare(int)

    with for_(n, 0, n < 1000, n + 1):
        with for_(f, f_min, f < f_max, f + df):

            update_frequency(rr, f)
            wait(rep_rate_clk - ro_len, rr)
            measure("readout", rr, None,
                    demod.full("integW_cos", I, out),
                    demod.full("integW_minus_sin", Q, out))

            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(freq_list)).average().save('I')
        Q_st.buffer(len(freq_list)).average().save('Q')

######################################
# Open Communication with the Server #
######################################
qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name)

####################
# Simulate Program #
####################
if simulate:
    simulation_config = SimulationConfig(
        duration=200000,
        simulation_interface=LoopbackInterface([("con1", 9, "con1", 1), ("con1", 10, "con1", 2)]))
    job = qmm.simulate(config, rr_spec, simulation_config)
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()
    raise Halted()

#############
# execution #
#############
qm = qmm.open_qm(config)
job = qm.execute(rr_spec)
job.result_handles.wait_for_all_values()
I = job.result_handles.get("I").fetch_all()
Q = job.result_handles.get("Q").fetch_all()

############
# analysis #
############
# plt.figure()
freq_list = 1e-9*(rr_LO_val + freq_list)
sig = I + 1j*Q
if len(zeros):
    freq_list = np.delete(freq_list, zero_i)
    sig = np.delete(sig, zero_i)

e_delay = elec_delay_ns[str(rr_no)]
p_offset = phase_offset_rad[str(rr_no)]
if check_e_delay:
    e_delay = elec_delay_ns[str(rr_no)]
    p_offset = phase_offset_rad[str(rr_no)]
# e_delay = 283.35
# p_offset = 6.484+2.284
sig_corrected = sig*np.exp(1j*2*np.pi*freq_list*e_delay + 1j*p_offset)
phase = np.angle(sig_corrected)
real = np.real(sig_corrected)
imag = np.imag(sig_corrected)
f_res_i = np.argmin(np.abs(sig))
f_res_i = np.argmin(np.abs(phase))
f_res = freq_list[f_res_i]
plt.plot(freq_list, phase)

plt.figure()
plt.plot(freq_list, phase)
plt.legend()
plt.xlabel("Frequency (GHz)")
plt.title(f'Cavity Spectroscopy (Phase) : Cavity Frequency = {f_res} GHz')
plt.axvline(x=f_res, linestyle = "--")
plt.grid()
plt.show(block=False)

if not check_e_delay:
    plt.figure()
    plt.plot(freq_list, real, label="Real")
    plt.plot(freq_list, imag, label="Imag")
    plt.title(f'Cavity Spectroscopy (Real) : Cavity Frequency = {f_res} GHz')
    plt.xlabel("Frequency (GHz)")
    plt.axvline(x=f_res, linestyle = "--")
    plt.grid()
    plt.legend()
    plt.show(block = False)

    plt.figure()
    plt.plot(freq_list, np.abs(sig))
    plt.title(f'Cavity Spectroscopy (Magnitude) : Cavity Frequency = {f_res} GHz')
    plt.xlabel("Frequency (GHz)")
    plt.axvline(x=f_res, linestyle="--")
    plt.grid()
    plt.show(block = False)

data = np.transpose([freq_list, phase, real, imag, np.abs(sig)])

if save_data and not check_e_delay:
    file_saver_qubit_(data, file_name=__file__, master_folder=ExpName,
                header_string="Frequency (GHz), Phase, Real, Imaginary, Magnitude", qubit=f"rr{rr_no}")
