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
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

save_data = True
rescale = False
update_pars = False
simulate = False
pi12 = False
SVM = True
qmm = QuantumMachinesManager(qm_ip, cluster_name=cluster_name)
q_no = 3
qe = f"q{q_no}"
rr = f"rr{q_no}"
out = adc_mapping[rr]

if simulate:
    rep_rate_clk = 300
    herald_delay = 300
else:
    rep_rate_clk = 500000
    herald_delay = 8000
wait_rr = 16
pi_len = pi_len_ns[str(q_no)]
ro_len = ro_len_clk[str(q_no)]

int_wt = 'opt'

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
    I0_st = declare_stream()
    Q0 = declare(fixed)
    Q0_st = declare_stream()
    I1 = declare(fixed)
    I1_st = declare_stream()
    Q1 = declare(fixed)
    Q1_st = declare_stream()
    I0_pre = declare(fixed)
    Q0_pre = declare(fixed)
    I1_pre = declare(fixed)
    Q1_pre = declare(fixed)
    I0_pre_st = declare_stream()
    Q0_pre_st = declare_stream()
    I1_pre_st = declare_stream()
    Q1_pre_st = declare_stream()


    with for_(n, 0, n < 10000, n + 1):
        reset_frame(qe, rr)
        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=pi12, dem=dem)
        if SVM:
            align([qe, rr])
            measure_macro_weight(qe, rr, out, I0_pre, Q0_pre, pi_12=pi12, weight_choice=int_wt)
            save(I0_pre, I0_pre_st)
            save(Q0_pre, Q0_pre_st)
            align(qe, rr)
            wait(herald_delay, [qe, rr])

        play("I", qe)
        # align(qe, rr)
        # wait(wait_rr, rr)
        # measure("readout" * amp(a_rr), rr, None,
        #         demod.full("integW_cos", I0, out),
        #         demod.full("integW_minus_sin", Q0, out))
        measure_macro_weight(qe, rr, out, I0, Q0, pi_12=pi12, weight_choice=int_wt)
        save(I0, I0_st)
        save(Q0, Q0_st)

        align()

        reset_frame(qe, rr)
        cooldown(time=rep_rate_clk, active_reset=False,
                 qe=qe, qe_12=None, rr=rr, out=out, I=I, Q=Q, pi_12=pi12, dem=dem)
        if SVM:
            align(qe, rr)
            measure_macro_weight(qe, rr, out, I1_pre, Q1_pre, pi_12=pi12, weight_choice=int_wt)
            save(I1_pre, I1_pre_st)
            save(Q1_pre, Q1_pre_st)

            wait(herald_delay, [qe, rr])
            align(qe, rr)

        # wait(rep_rate_clk, qe)
        play_X180(qe)
        # play("grft" * amp(0.15), qe, 22)
        # align(qe, rr)
        # wait(wait_rr, rr)
        # measure("readout" * amp(a_rr), rr, None,
        #         demod.full("integW_cos", I1, out),
        #         demod.full("integW_minus_sin", Q1, out))
        measure_macro_weight(qe, rr, out, I1, Q1, pi_12=pi12, weight_choice=int_wt)
        save(I1, I1_st)
        save(Q1, Q1_st)

    with stream_processing():
        I0_st.save_all('I0')
        Q0_st.save_all('Q0')
        I1_st.save_all('I1')
        Q1_st.save_all('Q1')
        if SVM:
            I0_pre_st.save_all('I0_pre')
            Q0_pre_st.save_all('Q0_pre')
            I1_pre_st.save_all('I1_pre')
            Q1_pre_st.save_all('Q1_pre')

qm = qmm.open_qm(config)

if simulate:
    job = qmm.simulate(config, IQ_blobs, SimulationConfig(int(10000)))
    # get DAC and digital samples
    samples = job.get_simulated_samples()
    # plot all ports:
    # samples.con1.plot()
    samples.con2.plot()
    plt.show(block=False)

    raise Halted()

job = qm.execute(IQ_blobs)

I0_handle = job.result_handles.get("I0")
Q0_handle = job.result_handles.get("Q0")
I1_handle = job.result_handles.get("I1")
Q1_handle = job.result_handles.get("Q1")

if SVM:
    I0_pre_handle = job.result_handles.get("I0_pre")
    Q0_pre_handle = job.result_handles.get("Q0_pre")
    I1_pre_handle = job.result_handles.get("I1_pre")
    Q1_pre_handle = job.result_handles.get("Q1_pre")

job.result_handles.wait_for_all_values()

I0 = I0_handle.fetch_all()["value"]
Q0 = Q0_handle.fetch_all()["value"]
I1 = I1_handle.fetch_all()["value"]
Q1 = Q1_handle.fetch_all()["value"]


if rescale:
    I0 = 1e6 * I0/ ro_len
    Q0 = 1e6 * Q0/ ro_len
    I1 = 1e6 * I1/ ro_len
    Q1 = 1e6 * Q1/ ro_len

angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(I0, Q0, I1, Q1, b_print=True, b_plot=True)
plt.show(block=False)
print(f"Ig, Ie = {np.mean(I0)}, {np.mean(I1)}")
print(f"Qg, Qe = {np.mean(Q0)}, {np.mean(Q1)}")




# Stack the I and Q coordinates into a 2D feature matrix
if SVM:

    I0_pre = I0_pre_handle.fetch_all()["value"]
    Q0_pre = Q0_pre_handle.fetch_all()["value"]
    I1_pre = I1_pre_handle.fetch_all()["value"]
    Q1_pre = I1_pre_handle.fetch_all()["value"]

    # --- 2. Format Data for the Model ---
    X_0 = np.column_stack((I0, Q0))
    y_0 = np.zeros(len(I0)) # Label all these as state 0

    X_1 = np.column_stack((I1, Q1))
    y_1 = np.ones(len(I1))  # Label all these as state 1

    # Combine them into the final dataset
    X = np.vstack((X_0, X_1))
    y = np.concatenate((y_0, y_1))

    # Split into 70% training data and 30% testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # --- 3. Train the SVM ---
    print("Training the SVM (RBF Kernel)...")
    # The RBF kernel allows the boundary to curve around the blobs
    svm = SVC(kernel='rbf', C=1.0, gamma='scale')
    svm.fit(X_train, y_train)

    # --- 4. Evaluate Fidelity ---
    y_pred = svm.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    # cm[0,0] is correctly identified |0>, cm[0,1] is false |1> (Thermal)
    # cm[1,1] is correctly identified |1>, cm[1,0] is false |0> (T1 Decay)
    fid_0 = cm[0, 0] / (cm[0, 0] + cm[0, 1])
    fid_1 = cm[1, 1] / (cm[1, 0] + cm[1, 1])
    avg_fid = (fid_0 + fid_1) / 2

    print(f"SVM |0> Fidelity (g -> g): {fid_0 * 100:.2f}%")
    print(f"SVM |1> Fidelity (e -> e): {fid_1 * 100:.2f}%")
    print(f"SVM Average Fidelity:      {avg_fid * 100:.2f}%")

    # --- 5. Plot the Decision Boundary ---
    plt.figure(figsize=(8, 6))

    # Create a mesh grid covering the data range
    x_min, x_max = X[:, 0].min() - 0.1*np.abs(X[:, 0].min()), X[:, 0].max() + 0.1*np.abs(X[:, 0].max())
    y_min, y_max = X[:, 1].min() - 0.1*np.abs(X[:, 1].min()), X[:, 1].max() + 0.1*np.abs(X[:, 1].max())
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300), np.linspace(y_min, y_max, 300))

    # Predict states across the entire grid to draw the boundary
    Z = svm.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Plot the background regions
    plt.contourf(xx, yy, Z, alpha=0.3, cmap='bwr')
    plt.contour(xx, yy, Z, colors='k', levels=[0.5], linewidths=2)

    # Scatter the testing data
    plt.scatter(X_test[y_test == 0][:, 0], X_test[y_test == 0][:, 1], color='blue', s=5, alpha=0.5, label='|0> Data')
    plt.scatter(X_test[y_test == 1][:, 0], X_test[y_test == 1][:, 1], color='red', s=5, alpha=0.5, label='|1> Data')


    plt.title(f"SVM Classification Boundary (Avg Fid: {avg_fid * 100:.2f}%)")
    plt.xlabel("I")
    plt.ylabel("Q")
    plt.legend()
    plt.show(block=False)

    herald_0 = np.column_stack((I0_pre, Q0_pre))
    herald_1 = np.column_stack((I1_pre, Q1_pre))

    herald_states_0 = svm.predict(herald_0)
    herald_states_1 = svm.predict(herald_1)

    valid_mask_0 = (herald_states_0 == 0)
    valid_mask_1 = (herald_states_1 == 0)

    filtered_final_I_0 = I0[valid_mask_0]
    filtered_final_Q_0 = Q0[valid_mask_0]

    filtered_final_I_1 = I1[valid_mask_1]
    filtered_final_Q_1 = Q1[valid_mask_1]

    # --- 5. Classify the Filtered Final Data ---
    X_final_0 = np.column_stack((filtered_final_I_0, filtered_final_Q_0))
    final_states_0 = svm.predict(X_final_0)

    X_final_1 = np.column_stack((filtered_final_I_1, filtered_final_Q_1))
    final_states_1 = svm.predict(X_final_1)

    # --- 6. Calculate True Heralded Fidelities ---
    # How many of the filtered |0> shots actually measured as 0?
    fid_0 = np.sum(final_states_0 == 0) / len(final_states_0)

    # How many of the filtered |1> shots actually measured as 1?
    fid_1 = np.sum(final_states_1 == 1) / len(final_states_1)

    avg_fid = (fid_0 + fid_1) / 2

    min_len = min(len(filtered_final_Q_1), len(filtered_final_Q_0))

    # --- 7. Print the Results ---
    print("--- Thermal Discard Rates ---")
    print(f"Thermal population before |0>: {100 * (1 - len(final_states_0) / len(I0)):.2f}%")
    print(f"Thermal population before |1>: {100 * (1 - len(final_states_1) / len(I1)):.2f}%")
    print("\n--- True Heralded Fidelities ---")
    print(f"|0> Fidelity (g -> g): {fid_0 * 100:.2f}%")
    print(f"|1> Fidelity (e -> e): {fid_1 * 100:.2f}%")
    print(f"Average Fidelity:      {avg_fid * 100:.2f}%")

    angle, threshold, fidelity, gg, ge, eg, ee = two_state_discriminator(filtered_final_I_0[:min_len], filtered_final_Q_0[:min_len], filtered_final_I_1[:min_len], filtered_final_Q_1[:min_len], b_print=True, b_plot=True)
    plt.show(block=False)
if update_pars:
    with open('../Configuration_Files/Readout_Settings/optimal_readout_phase.json', 'r') as f:
        rdout_phases = json.load(f)
        f.close()

    n_angle = rdout_phases[f'rr{q_no}'] + (-1 * angle * 180 / np.pi)

    rdout_phases[f'rr{q_no}'] = np.round(n_angle%360, 3)

    with open('../Configuration_Files/Readout_Settings/optimal_readout_phase.json', 'w') as f:
        json.dump(rdout_phases, f, indent=6)
        f.close()

    with open('../Configuration_Files/Readout_Settings/demarcations.json', 'r') as f:
        demarks = json.load(f)
        f.close()

    demarks[str(q_no)] = threshold

    with open('../Configuration_Files/Readout_Settings/demarcations.json', 'w') as f:
        json.dump(demarks, f, indent=6)
        f.close()

if save_data:
    file_saver_(np.transpose([I0, Q0, I1, Q1]), file_name=__file__,
                master_folder=ExpName, header_string="I0, Q0, I1, Q1")

