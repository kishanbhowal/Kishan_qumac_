import copy

import os
import threading
import numpy as np
import json
import subprocess
from matplotlib import pyplot as plt
from Configuration_Files.configuration_4qubitsv3 import *
from datetime import datetime
import csv

matplotlib.use('Qt5Agg')
from Helper_Functions.analysis_functions import *
from Helper_Functions.helper_functionsv2 import bulk_switch
from inputimeout import inputimeout, TimeoutOccurred
import subprocess
import qualang_tools as qt
q_no = 5
do_mixer_calib = 1
qe = f'q{q_no}'


def get_input(input_list):

    """Thread target function to get user input."""
    user_input = input("Enter something: ")
    input_list.append(user_input)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def coh_fit(t, A, d, c):
    return A * np.exp(-t / d) + c


####    Experiment starts

## Switch config for spectrum analyser
# qe_sw = f'q1'
qe_sw = qe
bulk_switch(qe=keyer(qe, dac_mapping), ip=sw_ip, switches=switches)

init_path = "./Scripts/"

tof = 'Calibration_TimeOfFlight_userin_auto_check'

try:
    subprocess.run(f'python {init_path + tof}.py {q_no}', check=True)
    # print('Disabling loopback. Some bug')
except:
    print('Exception occurred. Check')
    sys.exit()

conn_flag = 0

if os.path.exists('./loopback_tof.json'):
    with open('./loopback_tof.json', 'r') as f:
        flg = json.load(f)
        if flg[str(q_no)]['loopback']:
            conn_flag = 1
        else:
            conn_flag = 0
else:
    conn_flag = 0

if conn_flag:
    user_input = 1
    pass
else:
    print('Autoloopback shows failure. Proceed?')
    input_list = []
    input_thread = threading.Thread(target=get_input, args=(input_list,))
    input_thread.start()
    input_thread.join(timeout=10)
    if input_thread.is_alive():
        print('Next time, please decide in 10 seconds. For now....')
        user_input = 1
    else:
        user_input = input_list[0]

# time.sleep(10)

if user_input != '0':
    print('....Proceeding as if there are no issues')
else:
    print('Ok. Stopping')
    sys.exit()

init_path = "D:/Experiments/"

exp_rabi = 'TimeDomain_Rabi_user_in'

script_folder_path = './Scripts/'

now = datetime.now()
current_date = now.strftime("%y-%m-%d")

fin_path = init_path + ExpName + '/' + exp_rabi + '/' + current_date + f'_q{q_no}' + '/'

while True:
    try:
        subprocess.run(f'python {script_folder_path + exp_rabi}.py {q_no}', check=True)
    except:
        print('Exception occurred. Check')
        sys.exit()

    ###     Add plots

    rabi_file = os.listdir(fin_path)[-1]

    rabi_data = []

    with open(fin_path + rabi_file) as rabi:
        file = csv.reader(rabi)
        for row in file:
            rabi_data.append(row)

    rabi_data = np.transpose(rabi_data[1:])

    time = np.array(rabi_data[0], dtype=float)
    I = np.array(rabi_data[1], dtype=float)
    Q = np.array(rabi_data[2], dtype=float)

    with open('./Rabi_data_auto.json', 'r') as f:
        fit_data = json.load(f)
        f.close()

    I_fit = [rabi_fit(i, fit_data['fit_data_I']['amp'], fit_data['fit_data_I']['freq'], 1e6,
                      fit_data['fit_data_I']['phase'] + np.pi / 2, fit_data['fit_data_I']['offset']) for i in time]

    Q_fit = [rabi_fit(i, fit_data['fit_data_Q']['amp'], fit_data['fit_data_Q']['freq'], 1e6,
                      fit_data['fit_data_Q']['phase'] + np.pi / 2, fit_data['fit_data_Q']['offset']) for i in time]

    plt.ion()
    fig, axs = plt.subplots(2, 1, sharex=True)
    manager = plt.get_current_fig_manager()
    manager.window.showMaximized()

    data = {"I": [I, fit_data['fit_data_I']], "Q": [Q, fit_data['fit_data_Q']]}

    for i, ax in enumerate(axs.flat):
        ax.cla()
        data_label = list(data.keys())[i]
        plot_data = data[data_label]
        ax.plot(time, plot_data[0], marker='.', label=data_label)
        if data_label == 'I':
            ax.plot(time, I_fit, label=data_label + "_Fit")
        else:
            ax.plot(time, Q_fit, label=data_label + "_Fit")
        ax.set(xlabel="Time (ns)", ylabel="Rabi Amplitude")
        ax.legend()
        ax.grid()
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    plt.show(block=False)
    plt.pause(3)
    plt.close()
# fig.canvas.draw()  # Draw the updates
# plt.gcf().canvas.flush_events()  # Flush the GUI events

