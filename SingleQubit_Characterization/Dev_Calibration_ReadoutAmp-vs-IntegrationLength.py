from qm import SimulationConfig
from qm.qua import *
from qm import LoopbackInterface
from qm import QuantumMachinesManager
from Configuration_Files.configuration_4qubitsv3 import *
import numpy as np
#import matplotlib
#matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
from qualang_tools.analysis.discriminator import two_state_discriminator
# from qm import generate_qua_script

simulate = False
save_data = True
qmm = QuantumMachinesManager(host=qm_ip, cluster_name=cluster_name)
qm = qmm.open_qm(config)

q_no = 6
qe = f"q{q_no}"
rr = f"rr{q_no}"
qe_pump= f"rr{q_no}"

#============================
out = adc_mapping[rr]
chunk_size = 50 # In no. of clck cycles (units of 4ns) , determines integration length step size in clcls
integ_len = integ_len_clk[str(q_no)]
arr_size = int(integ_len/chunk_size)
n_runs = 1e4 # No. Of shots

ro_amp = ro_amp[str(q_no)]
if ro_amp != 1.0:
    print("Please set the ro_amp = 1.0 in config")
    raise Halted()
#ro_amp = ro_amp["2"]

a_min = 0.005
a_max = 0.3
da = 0.005

amps = np.arange(a_min, a_max + da/2, da)
#amps = np.sqrt(Power_array)
n_amps = amps.size

rep_rate_clk = 250000
if simulate :
    rep_rate_clk = 100
    n_runs = 1
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
ro_len = ro_len_clk[str(q_no)]
#ro_len = ro_len_clk["2"]
###################
# The QUA program #
###################
time_start  = time.time()
dem = -1.742e-3
a_rr = 1.0

with program() as IQ_blobs:

    n = declare(int)
    #j = declare(fixed)
    a = declare(fixed)
    I0 = declare(fixed, size=arr_size)
    I0_st = declare_stream()
    Q0 = declare(fixed, size=arr_size)
    Q0_st = declare_stream()
    I1 = declare(fixed, size=arr_size)
    I1_st = declare_stream()
    Q1 = declare(fixed, size=arr_size)
    Q1_st = declare_stream()

    #with for_(a, a_min, a < a_max + da / 2, a + 1):
    #with for_(j, 0, j < n_amps, j + 1):
    with for_each_(a, amps):
        with for_(n, 0, n < n_runs, n + 1):

            #reset_phase(rr)
            wait(rep_rate_clk, qe)
            play("I", qe)
            align(qe, qe_pump,rr)
            wait(wait_rr, rr)
            measure("readout"*amp(a), rr, None,
                    demod.accumulated("integW_cos", I0, chunk_size, out),
                    demod.accumulated("integW_minus_sin", Q0, chunk_size, out))
            for i in range(arr_size):
                save(I0[i], I0_st)
                save(Q0[i], Q0_st)

            align(rr, qe)
            #reset_phase(rr)
            wait(rep_rate_clk, qe)
            play("X180", qe)
            align(qe, qe_pump,rr)
            wait(wait_rr, rr)
            measure("readout"*amp(a) , rr, None,
                    demod.accumulated("integW_cos", I1, chunk_size, out),
                    demod.accumulated("integW_minus_sin", Q1, chunk_size, out))
            for i in range(arr_size):
                save(I1[i], I1_st)
                save(Q1[i], Q1_st)

    with stream_processing():
        I0_st.save_all('I0')
        Q0_st.save_all('Q0')
        I1_st.save_all('I1')
        Q1_st.save_all('Q1')

if simulate:
    job = qmm.simulate(config, IQ_blobs, SimulationConfig(int(4*22800)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    samples.con1.plot()
    raise Halted()

job = qm.execute(IQ_blobs)

I0_handle = job.result_handles.get("I0")
Q0_handle = job.result_handles.get("Q0")
I1_handle = job.result_handles.get("I1")
Q1_handle = job.result_handles.get("Q1")
job.result_handles.wait_for_all_values()

n_runs = int(n_runs)
arr_size = int(arr_size)
# I0 = I0_handle.fetch(slice(0, arr_size*n_runs))["value"]
# I1 = I1_handle.fetch(slice(0, arr_size*n_runs))["value"]
# Q0 = Q0_handle.fetch(slice(0, arr_size*n_runs))["value"]
# Q1 = Q1_handle.fetch(slice(0, arr_size*n_runs))["value"]
#
# I0_2d = np.transpose(I0.reshape(n_runs, arr_size))
# I1_2d = np.transpose(I1.reshape(n_runs, arr_size))
# Q0_2d = np.transpose(Q0.reshape(n_runs, arr_size))
# Q1_2d = np.transpose(Q1.reshape(n_runs, arr_size))

I0 = I0_handle.fetch_all()["value"]
Q0 = Q0_handle.fetch_all()["value"]
I1 = I1_handle.fetch_all()["value"]
Q1 = Q1_handle.fetch_all()["value"]

def reshape(A, n_amps, n_runs, arr_size):

    A_reshaped = A.reshape(n_amps, n_runs, arr_size)
    A_reshaped_transpose = []
    for i, a in enumerate(A_reshaped):
        A_reshaped_transpose.append(np.transpose(a))

    A_reshaped_transpose = np.array(A_reshaped_transpose)


    return A_reshaped_transpose

def get_fidelity(I0, Q0, I1, Q1):

    angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1,
                                                                         b_print=False, b_plot=False)
    return fidelity

def get_fidelity_list(I0_2d, Q0_2d, I1_2d, Q1_2d):

    fidelity_list = []
    for i in range(arr_size):
        fid = get_fidelity(I0_2d[i], Q0_2d[i], I1_2d[i], Q1_2d[i])
        fidelity_list.append(fid)
    return fidelity_list


I0_3d = reshape(I0, n_amps, n_runs, arr_size)
Q0_3d = reshape(Q0, n_amps, n_runs, arr_size)
I1_3d = reshape(I1, n_amps, n_runs, arr_size)
Q1_3d = reshape(Q1, n_amps, n_runs, arr_size)

fid_list_arr = []
for i, a in enumerate(amps):

    I0_2d, Q0_2d = I0_3d[i], Q0_3d[i]
    I1_2d, Q1_2d = I1_3d[i], Q1_3d[i]

    a = np.round(a, 3)
    if save_data is True:
        file_saver_(I0_2d, file_name=__file__, suffix=f"_wo_20dB_I02d_Amp_{a}", master_folder=ExpName, time_stamp=False) #_wo_20dB_
        file_saver_(Q0_2d, file_name=__file__, suffix=f"_wo_20dB_Q02d_Amp_{a}", master_folder=ExpName, time_stamp=False)
        file_saver_(I1_2d, file_name=__file__, suffix=f"_wo_20dB_I12d_Amp_{a}", master_folder=ExpName, time_stamp=False)
        file_saver_(Q1_2d, file_name=__file__, suffix=f"_wo_20dB_Q12d_Amp_{a}", master_folder=ExpName, time_stamp=False)

    fidelity_list = get_fidelity_list(I0_2d, Q0_2d, I1_2d, Q1_2d)
    fid_list_arr.append(fidelity_list)

fid_list_arr = np.array(fid_list_arr)
fid_list_2d = fid_list_arr.reshape(n_amps, arr_size)

plt.figure()
for i, arr in enumerate(fid_list_2d):
    plt.plot(arr,label= f'amps = {amps[i]}' )
plt.legend()
plt.show(block=False)

if save_data is True:
    file_saver_(fid_list_2d, file_name=__file__, suffix=f"Fidelity_AmpIntLen_2dSweep_qubit{q_no}", master_folder=ExpName, time_stamp=True)
time_end = time.time()
mins, secs = divmod(time_end - time_start, 60)
print(f"Execution time taken: {mins}m {secs}s")


