from Bluefors_config_builder_CPMG import *
from qualang_tools.units import unit
from instrumentlib import RhodeandSchwarz_SGS100A
import matplotlib
import json
from qm.octave import *
from qm.octave.octave_manager import ClockMode
import os

##################################################################
#ONLY SRIJITA/JAY ALLOWED TO MAKE CHANGES IN THIS FILE!!!!!!!!!!!!
##################################################################

u = unit()
matplotlib.use('Qt5Agg')
# matplotlib.use('Qt5Cairo')


TOF_testing =False
# ExpName = r"2024-02-10 2DRX08-qubitE"
ExpName = "2025-06-06 Quantromon DT08/Sriju_CPMG/QubitC"
#ExpName = "2025-05-16 QuantroDT06, INDIQ17G\INDIQ17G\OPX, Octave"
# Start of edit by Aneesh
n_qubits = 4
use_drag = False
# End of edit by Aneesh

qm_ip = "192.168.0.106"
octave_port = 11253  # Must be 11xxx, where xxx are the last three digits of the Octave IP address
con = "con1"
octave = "octave1"
cluster_name = "Blufors"
octave_config = QmOctaveConfig()
# Specify where to store the outcome of the calibration (correction matrix, offsets...)
octave_config.set_calibration_db(os.getcwd())
# Add an Octave called 'octave1' with the specified IP and port
octave_config.add_device_info(octave, qm_ip, octave_port)

# ====================== DAC Mapping ========================================
dac_mapping = {"q1": [1, [3, 4]], "q3": [1, [5, 6]], "q2": [1, [7, 8]],
               "q4": [1, [5, 6]], "rr2": [1, [1, 2]], "rr3": [1, [9, 10]],
               "rr1": [1, [1, 2]],"rr4": [1, [9, 10]],
               "cr_c2t1": [1, [7, 8]], "cr_c3t1": [1, [3, 4]], "cr_c3t2": [1, [5, 6]], "cr_c4t3": [1, [3, 4]],
               "cz_c3t1": [1, [3, 4]], "cz_c2t1": [1, [7, 8]], "cz_c3t2": [1, [5, 6]], "cz_c2t3": [1, [3, 4]],
               "siz_2": [1, [7, 8]], "siz_3": [1, [3, 4]], "cz_2": [1, [7, 8]], "cz_3": [1, [3, 4]], "siz_4": [1, [7, 8]]}

octave_outputs = {"rr1": 1, "q1": 2, "rr3": 5, "q3": 3,
                  "rr2": 1, "q2": 4, "q4": 3, "rr4": 5
                  }
octave_inputs = {"rr1": 1, "rr3": 2, "rr2": 2, "rr4": 2,
                 }

adc_mapping = {"rr1": "out1", "rr3": "out2", "rr2": "out2",
               "rr4": "out2"}

# =======================Frequencies==========================================

qe_list = ["q1", "q2", "q3", "q4",
           "rr1", "rr2", "rr3", "rr4",
           "cr_c2t1", "cr_c3t1", "cr_c3t2", "cr_c4t3","cz_c3t1","cz_c3t2",
           "cz_c2t3","q12_1", "q12_2", "q12_3", "q12_4"]

CrossKerr = {"1": (0*0.078 + 0*0.06675) * u.MHz,
             "2": (0*0.195 + 0*0.06675) * u.MHz,
             "3": (0*0.078 + 0*0.195) * u.MHz,
             "4": 0*0.1255 * u.MHz,
             }

q_LO = {"1": 4.3 * u.GHz, #4.2
        "2": 4.3 * u.GHz,
        "3": 4.3 * u.GHz,
        "4": 4.3 * u.GHz,
        }

siz_correct_IF = {"1": 0 * u.MHz,
                  # "2": 1 * (3.969 * u.MHz + 0.12430 * u.MHz), #4.4699 #40MHz below
                  # "3": 1 * 0.500 * u.MHz, #40 MHz below
                  "2": 0 * (-1.631 * u.MHz + 1.5 * u.MHz),
                  "3": 0 * (-3.0082 * u.MHz + 0.2 * u.MHz),
                  "4": 0 * u.MHz,
                 }

q_IF = {"1": 318.580 * u.MHz + CrossKerr["1"],  #418.59949  218.73  318.5990  318.3870
        "2": 166.09 * u.MHz + CrossKerr["2"] + siz_correct_IF["2"], #QubitB 164.590
        "3": 221.81 * u.MHz + CrossKerr["3"] + siz_correct_IF["3"], #Qubit E 219.632
        "4": 80.288 * u.MHz + CrossKerr["4"]
         }

cz_IF = {"1": 0 * u.MHz,
        "2": 0 * u.MHz, #q_IF["2"] - 0 * 40 * u.MHz, #QubitB 164.590
        "3": 0 * u.MHz, #q_IF["2"] - 0 * 40 * u.MHz, #Qubit E 219.632
        "4": 0 * u.MHz
         }


raman_IF = {"1": 0 * u.MHz,
            # "2": 19.7378 * u.MHz - 4.50 * u.MHz, #q_IF["2"] - 0 * 40 * u.MHz, #QubitB 164.590
            # "3": 19.7378 * u.MHz - 4.50 * u.MHz, #q_IF["2"] - 0 * 40 * u.MHz, #Qubit E 219.632
            "2": -138.656 * u.MHz,
            "3": 21.45 * u.MHz,
            "4": 0 * u.MHz
         }

# Start of edit by Aneesh
q_anh = {"1": -252 * u.MHz, #220
         "2": -248 * u.MHz ,
         "3": -248.40 * u.MHz, #204

         "4": -300 * u.MHz
        }
# End of edit by Aneesh
rr_LO = {"1": 7.6186* u.GHz, #7.6193
         "2": 7.415 * u.GHz,
         "3": 7.12725 * u.GHz,
         "4": 7.12725 * u.GHz
         }

rr_IF = {"1": 20.0 * u.MHz,
         "2": 20.0 * u.MHz,
         "3": 30.0 * u.MHz,
         "4": 0.0 * u.MHz
         }

round_freq_dicts([CrossKerr, q_LO, q_IF, rr_LO, rr_IF])
# ======================Readout Parameters===========================================
tof = {"1": 752,
       "2": 712, #712
       "3": 500,  #300
       "4": 300
       }

gain = {"1" : {"1": 10, "2": 10},  #Set ADC gain here
        "2" : {"1": 10, "2": 10}}

ro_len_clk = {"1": 1000,
              "2": 800, #2000
              "3": 800,
              "4": 400
              }

integ_len_clk = {"1": 500, #600
                 "2": 550,
                 "3": 600, #480
                 "4": 400
                 }

ro_amp = {"1": 0.032, #QubitC 0.044 (max)
          "2": 0.045,#QubitB 0.048
          "3": 0.088, #QubitE #0.09
          "4": 0.300 #Pump for Qubit 2  0.487
          }

# For TOF Testing
if TOF_testing:

    ro_amp = {"1": 1.0,
              "2": 1.0,
              "3": 1.0,
              "4": 1.0
              }

    rr_IF = {"1": 12 * u.MHz,
             "2": 12 * u.MHz,
             "3": 12 * u.MHz,
             "4": 12 * u.MHz
             }

optimal_readout_phase = {"rr1": (295)*(np.pi/180), # add 150for paramp  PJ: -75
                         "rr2": (5+6.7)*(np.pi/180),#150 for no paramp
                         "rr3": (24-5.8)*(np.pi/180),
                         "rr4": (-60)*(np.pi/180)
                         }

demarcations = {"1": -2.880e-04,
                "2": -1.690e-04, #5.475e-05,
                "3": 1.255e-03,  #5.109e-05,
                "4": 5.109e-05
                }

eta_readout = { "1": 1.0,
                "2": 0.483, #5.475e-05,
                "3": 0.268,  #5.109e-05,
                "4": 1.0
                }


elec_delay_ns = {"1": 279.095, #251.922 279.1  #279.155 without DS
                "2": 269.80,
                "3": 265,
                "4": 252.3
                }

phase_offset_rad = {"1": 4.987+1.142,
                    "2": -2,
                    "3": 5.0,
                    "4": 6.568
                    }

# if attenuator:
#     ro_amp = {"2": 0.5}
#     optimal_readout_phase = {"rr2":-120*(np.pi/180)}


# ==================Control Parameters===============================================

pi_rise_grft_ns = 10
pi_len_ns = {"1": 52,  #52
             "2": 180,  #200
             "3": 52, #52 #100 #40

             "4": 100,
             }

piby2_rise_grft_ns = 10
#Keep piby2 len fixed and calibrate amplitude using power rabi instead of changing length to half
piby2_len_ns = {"1": 52, #52
                "2": 180, #200
                "3": 52,#52 #100 #40

                "4": 100,
                }
cr_tail_ns = 16
cr_len_ns = {"cr_c2t1": 336,
             "cr_c3t1": 152, #152
             "cr_c3t2": 120,
             "cr_c4t3": 576,
             }


cr_amp = {"cr_c2t1": -0.3, "cr_ac_c2t1": 0.03,
          "cr_c3t1": 1.0, "cr_ac_c3t1": -0.2672, #-0.267
          "cr_c3t2": 1.0, "cr_ac_c3t2": 0.03,
          "cr_c4t3": 0.08, "cr_ac_c4t3": 0.03
          }

cr_phase = {"cr_c2t1":   0.4474474474474474, "cr_ac_c2t1": 0.13713713713713713,
            # "cr_c3t1": 0.14314314314314314-0.06,  "cr_ac_c3t1": 0.1061061061061061-0.06,
            "cr_c3t1": 0.05556, "cr_ac_c3t1":  0.0185229629,
            "cr_c3t2":   0.13113113113113112, "cr_ac_c3t2": -0.07307307307307309, #after IZ correction
            # "cr_c3t2":   0.020020020020020016, "cr_ac_c3t2": -0.058058058058058054, #before IZ correction
            # "cr_c3t2":   0.525, "cr_ac_c3t2": -0.06,  #-
            "cr_c4t3":   0.4734734734734734, "cr_ac_c4t3": 0.03003003003003002
            }

# For Power Rabi amplitude calibration
'''
calib_vals = {"1": {"amin": 0.46, "amax": 0.52, "da": 0.0005, "n_pulses": 13},
              "2": {"amin": 0.295, "amax": 0.318, "da": 0.0001, "n_pulses": 17},
              "3": {"amin": 0.35, "amax": 0.50, "da": 0.001, "n_pulses": 7},
              "4": {"amin": 0.12, "amax": 0.126, "da": 0.00005, "n_pulses": 17}
              }


amp_scale = {
             "1": {"X180": 0.420560, "Y180": 0.420560, "X90": 0.330130, "Y90": 0.330130},
             # "2": {"X180": 0.532481, "Y180": 0.532481, "X90": 0.264837, "Y90": 0.264837},
             #"2": {"X180": 0.536628, "Y180": 0.536628, "X90": 0.266308, "Y90": 0.266308},
             "2": {"X180": 0.546343, "Y180": 0.546613, "X90": 0.270253, "Y90": 0.270245},
             #"3": {"X180": 0.493297, "Y180": 0.493297, "X90": 0.240145, "Y90": 0.240145},
             # "3": {"X180": 0.583227, "Y180": 0.582509, "X90": 0.294219, "Y90": 0.293995}, #before setting 8dB gain in RF2, 0dB gain amps
             "3": {"X180": 0.301987, "Y180": 0.301998, "X90": 0.149195, "Y90": 0.149210}, #after setting 8dB gain, but got wrong pi pulse
             # "3": {"X180": 0.304092, "Y180": 0.304092, "X90": 0.150075, "Y90": 0.150075},
             "4": {"X180": 0.299, "Y180": 0.299459, "X90": 0.1501700, "Y90": 0.1501},
             "5": {"X180": 0.1376, "Y180": 0.137678839419, "X90": 0.068866933466, "Y90": 0.068866933466},
             "6": {"X180": 0.09830, "Y180": 0.0983091545772, "X90": 0.049184592296, "Y90": 0.049184592296},
             "7": {"X180": 0.91, "Y180": 0.91895947973, "X90": 0.470825412706, "Y90": 0.470825412706},
             "8": {"X180": 0.21113, "Y180": 0.211, "X90": 0.10647823, "Y90": 0.10647},
             }
'''
# ------- Start of edit by Aneesh -------

# For ORBIT amplitude and DRAG calibration
amp_scale = {}
drag_dict = {}
q_no_list = [i+1 for i in range(n_qubits)]

for q_i in q_no_list:
    vars()[f"amp_pi_{q_i}"] = 1 # TO BE UPDATED AFTER ROUGH AMP CALIB
    vars()[f"amp_piby2_{q_i}"] = 1 # TO BE UPDATED AFTER ROUGH AMP CALIB
    vars()[f"alpha_{q_i}"] = 0 # SET 1 FOR QUBIT BEFORE DRAG CALIB
    vars()[f"det_{q_i}"] = 0 # in MHz

'''
# Hardcode calib values here if necessary
'''
# #For Qubit1
# #-------------------------------------------------------
det_1 = 0.0
alpha_1 = 1.6617 #1.7507
##--------------------------------------------------------
# #For Qubit2
# #-----------------------------------------------
det_2 = 0.0
alpha_2 = 11.3721 # 11.2217# 10.9759 #11.2403
# alpha_2 = 5.3906 #With adding cross-Kerr
# #--------------------------------------------------------
# #For Qubit3
det_3 = 0.0
alpha_3 = 0.0
# #--------------------------------------------------------

for q_i in q_no_list:
    if not f"{q_i}" in amp_scale: 
        amp_scale[f"{q_i}"] = {}
    amp_scale[f"{q_i}"]["X180"] = eval(f"amp_pi_{q_i}")
    amp_scale[f"{q_i}"]["Y180"] = eval(f"amp_pi_{q_i}")
    amp_scale[f"{q_i}"]["X90"] = eval(f"amp_piby2_{q_i}")
    amp_scale[f"{q_i}"]["Y90"] = eval(f"amp_piby2_{q_i}")

    if not f"{q_i}" in drag_dict:
        drag_dict[f"{q_i}"] = {}
    drag_dict[f"{q_i}"]["alpha"] = eval(f"alpha_{q_i}")
    drag_dict[f"{q_i}"]["det"] = eval(f"det_{q_i}") * u.MHz


#Power rabi calibrations
#qubit 1 52ns(10ns)
amp_scale['1']["X180"] = 0.709780 #0.6008,  0.383792  0.707354
amp_scale['1']["Y180"] = 0.709780 #0.6008
amp_scale['1']["X90"] = 0.342160 #0.289645,  0.190295  0.339620
amp_scale['1']["Y90"] = 0.342160 #0.289645

amp_scale['2']["X180"] = 0.165893 #0.16693
amp_scale['2']["Y180"] = 0.165893 # 0.16658
amp_scale['2']["X90"] = 0.081425 #0.083057
amp_scale['2']["Y90"] = 0.081449 #0.083070


# #qubit 3 52ns(10ns)
amp_scale['3']["X180"] = 0.48631 #0.49178
amp_scale['3']["Y180"] = 0.485732 #0.49119
amp_scale['3']["X90"] = 0.23878 #0.241727
amp_scale['3']["Y90"] = 0.23884 #0.241530


siz_IF = {"1": 0.0 * u.MHz,
         "2": 240 * u.MHz, #164.547 * u.MHz - 40 * u.MHz,
         "3": 240 * u.MHz, #164.547 * u.MHz - 40 * u.MHz
         "4": 0 * u.MHz
          }

# ------ End of edit by Aneesh -------

# =================== Dictionaries for 1-2 transition =================================

q12_LO = { "1": 4.3 * u.GHz
         }

q12_IF = {"1": 90.9902 * u.MHz, #91.18
          "2": -83.166 * u.MHz,
          "3": -26.59 * u.MHz,

          "4": 80.288 * u.MHz,
         }

piby2_12_len_ns = {"1":80,#256,
                "2": 60,
                "3": 52,

                "4": 124,
                }

pi_12_len_ns = {"1": 80, #256,
                "2": 60,
                "3": 52,

                "4": 124,
                }

amp_12_scale = {"1": {"X180": 0.56888444, "Y180": 0.56888444, "X90": 0.27493746, "Y90": 0.27493746},
                "2": {"X180": 0.257898, "Y180": 0.257898, "X90":  0.118984, "Y90":  0.118984},
                "3": {"X180": 0.2433316, "Y180": 0.2433316, "X90":  0.110130, "Y90":  0.110130},  #0.5981540770
                "4": {"X180": 0.03908, "Y180": 0.1104652326, "X90": 0.05494747, "Y90": 0.05494747}, #0.1233579289
                }

# ==================Mixer Parameters ===============================================
# =================== DC Offsets ===============================================
with open('./Calibrations/dc_offsets.json') as f:
    dc_offsets = json.load(f)

# ================ List of Mixers ===============================================
mixers = {}
for qe in qe_list:
    mixers[qe] = "mixer_" + qe

# ================ IQ Imbalance Correction Matrices ===============================================
with open('./Calibrations/iq_imbalance.json') as f:
    iq_imbalance = json.load(f)

mixer_corrections = {}
for qe in qe_list:
    a = iq_imbalance[qe]["a"]
    p = iq_imbalance[qe]["p"]
    mixer_corrections[qe] = IQ_imbalance(a, p)

# ============== ADC Offets ===============================================
with open('./Calibrations/adc_offsets.json') as f:
    adc_offsets = json.load(f)

# ======================== QM Config Starts Here =========================================

config = {

    "version": 1,
}

config = config_add_controller(config, 1, dc_offsets, adc_offsets, gain["1"])
config = config_add_common_elements(config, q_LO, rr_LO)

# NOTE only 3 qe necessary in this experiment
n_qubits = 4
for i in range(1, n_qubits+1):
    q_no = i
    rr_no = i

    if use_drag:
        config = config_add_drag_elements_q_rr(config, q_no, rr_no, dac_mapping, octave_outputs, octave_inputs,  q_LO, q_IF, q_anh, rr_LO, rr_IF, pi_len_ns, piby2_len_ns, pi_rise_grft_ns, amp_scale,
                                           drag_dict, mixers, mixer_corrections, ro_amp, ro_len_clk, tof, integ_len_clk, optimal_readout_phase, smearing=0)
    else:
        config = config_add_elements_q_rr(config, q_no, rr_no, dac_mapping, octave_outputs, octave_inputs, q_LO, q_IF, rr_LO, rr_IF, pi_len_ns, piby2_len_ns, pi_rise_grft_ns, amp_scale,
                                      mixers, mixer_corrections, ro_amp, ro_len_clk, tof, integ_len_clk, optimal_readout_phase, smearing=0)

# config = config_add_q12(config, 4, dac_mapping, octave_outputs, q_LO, q12_IF,
#                    pi_12_len_ns, piby2_12_len_ns, pi_rise_grft_ns, amp_12_scale, mixers, mixer_corrections, use_octave=False)


config = config_add_rise_fall(config, cr_tail_ns)
# Check CR config elements
config = config_add_crgate(config, 2, 1, dac_mapping, q_LO, q_IF, mixers, mixer_corrections,octave,octave_outputs)
config = config_add_crgate(config, 3, 1, dac_mapping, q_LO, q_IF, mixers, mixer_corrections,octave,octave_outputs)
config = config_add_crgate(config, 3, 2, dac_mapping, q_LO, q_IF, mixers, mixer_corrections, octave, octave_outputs)
# config = config_add_crgate(config, 4, 3, dac_mapping, q_LO, q_IF, mixers, mixer_corrections)

# Check CZ config elements
config = config_add_czgate(config, 3, 1, dac_mapping, q_LO, q_IF, raman_IF ,mixers, mixer_corrections, octave, octave_outputs)
config = config_add_czgate(config, 3, 2, dac_mapping, q_LO, q_IF, raman_IF ,mixers, mixer_corrections, octave, octave_outputs)
config = config_add_czgate(config, 2, 3, dac_mapping, q_LO, q_IF, raman_IF ,mixers, mixer_corrections, octave, octave_outputs)

#Add quantum elements for 1-2 transition
n_qubits = 4
for i in range(1, n_qubits+1):

    q_no = i
    config = config_add_q12(config, q_no, dac_mapping, octave_outputs, q_LO, q12_IF,q12_LO,
                   pi_12_len_ns, piby2_12_len_ns, pi_rise_grft_ns, amp_12_scale, mixers, mixer_corrections)

#
# #Add SIZZLE GAtes
config = config_add_sizzle(config, 2, dac_mapping, siz_IF, mixers, mixer_corrections, octave, octave_outputs)
config = config_add_sizzle(config, 3, dac_mapping, siz_IF, mixers, mixer_corrections, octave, octave_outputs)
config = config_add_sizzle(config, 4, dac_mapping, siz_IF, mixers, mixer_corrections, octave, octave_outputs)

# #Add CZ_SIZZLE GAtes
config = config_add_cz_sizzle(config, 2, dac_mapping, cz_IF, mixers, mixer_corrections, octave, octave_outputs)
config = config_add_cz_sizzle(config, 3, dac_mapping, cz_IF, mixers, mixer_corrections, octave, octave_outputs)
