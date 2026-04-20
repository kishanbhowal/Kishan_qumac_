from helper_functionsv2_CPMG import *

##################################################################
#ONLY SRIJITA/JAY ALLOWED TO MAKE CHANGES IN THIS FILE!!!!!!!!!!!!
##################################################################

def config_add_controller(config, con_no, dc_offsets, adc_offsets, gain):

    if not "controllers" in config: config["controllers"] = {}

    config["controllers"][f"con{con_no}"] = {}
    config["controllers"][f"con{con_no}"]["type"] = "opx1"
    config["controllers"][f"con{con_no}"]["analog_outputs"] = {}

    for i in range(1, 11):
        config["controllers"][f"con{con_no}"]["analog_outputs"][i] = {"offset" : dc_offsets[f"con{con_no}"][f"{i}"]}

    config["controllers"][f"con{con_no}"]["digital_outputs"] = {}
    config["controllers"][f"con{con_no}"]["analog_inputs"] = {}

    for i in range(1, 3):
        config["controllers"][f"con{con_no}"]["analog_inputs"][i] = {"offset": adc_offsets[f"con{con_no}"][f"{i}"], 'gain_db': gain[f"{i}"]}

    return config

def config_add_common_elements(config, q_LO, rr_LO, octave="octave1", con="con1"):

    config["pulses"] = {"zero": {"operation": "control",
                                 "length": 100,
                                 "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
                                 },

                        "const_pulse": {
                            "operation": "control",
                            "length": 100,
                            "waveforms": {"I": "const_wf", "Q": "zero_wf"},
                        },
                        }

    config["waveforms"] = {"zero_wf": {"type": "constant", "sample": 0.0},
                           "const_wf": {"type": "constant", "sample": 0.4},
                           }

    config["digital_waveforms"] = {"ON": {"samples": [(1, 0)]}}

    config["octaves"] =  {
        octave: {
            "RF_outputs": {
                1: {
                    "LO_frequency": rr_LO["1"],
                    "LO_source": "internal",
                    "output_mode": "always_on",
                    # can be: "always_on" / "always_off"/ "triggered" / "triggered_reversed". "always_off" is the default
                    "gain": 0,  # can be in the range [-20 : 0.5 : 20]dB
                },
                2: {
                    "LO_frequency": q_LO["1"],
                    "LO_source": "internal",
                    "output_mode": "always_on",
                    "gain": 0,
                },
                3: {
                    "LO_frequency": q_LO["2"],
                    "LO_source": "internal",
                    "output_mode": "always_off",
                    "gain": 0,
                },
                4: {
                    "LO_frequency": rr_LO["2"],
                    "LO_source": "internal", #change this to external (connect Synth2 to this at the back)
                    "output_mode": "always_off",#"output_mode": "always_on",
                    "gain": 0, #12
                },
                5: {
                    "LO_frequency": rr_LO["2"],
                    "LO_source": "internal",
                    "output_mode": "always_off",#"output_mode": "always_off",
                    "gain": 0,
                },
            },
            "RF_inputs": {
                1: {
                    "LO_frequency": rr_LO["1"],  #Change to 1 when using rr1
                    "LO_source": "internal",  # internal is the default
                    "IF_mode_I": "direct",  # can be: "direct" / "mixer" / "envelope" / "off". direct is default
                    "IF_mode_Q": "direct",
                },
                2: {
                    "LO_frequency": rr_LO["2"],
                    "LO_source": "external",  # external is the default
                    "IF_mode_I": "direct",
                    "IF_mode_Q": "direct",
                },
            },
            "connectivity": con,
        }
    }

    return config

def config_add_elements_q_rr(config, q_no, rr_no, dac_mapping, octave_outputs, octave_inputs,  q_LO, q_IF, rr_LO, rr_IF, pi_len_ns, piby2_len_ns, pi_rise_grft_ns, amp_scale,
                     mixers, mixer_corrections, ro_amp, ro_len_clk, tof, integ_len_clk, optimal_readout_phase, smearing=0, use_octave=True, use_octave_input=True, octave="octave1"):
    '''
    Given parameters, this function adds the qubit, readout resonator, and all the standard pulses and waveforms to the config.
    '''

    ################ ADD ELEMENTS ################
    # Add qubit
    if not "elements" in config: config["elements"] = {}
    config['elements'][f"q{q_no}"] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][0]),
        #     "Q": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][1]),
        #     "lo_frequency": q_LO[f"{q_no}"],
        #     "mixer": mixers[f"q{q_no}"],
        # },
        "RF_inputs": {"port": (octave, octave_outputs[f"q{q_no}"])},
        "intermediate_frequency": q_IF[f"{q_no}"],
        "operations": {
            "const": "const_pulse",
            "Xgrft": f"q{q_no}_Xgrft",
            "Ygrft": f"q{q_no}_Ygrft",
            "X180": f"q{q_no}_X180",
            "X90": f"q{q_no}_X90",
            "mX90": f"q{q_no}_mX90",
            "X90C1": f"q{q_no}_X90C1",
            "X90C2": f"q{q_no}_X90C2",
            "X90C3": f"q{q_no}_X90C3",
            "Y180": f"q{q_no}_Y180",
            "Y90": f"q{q_no}_Y90",
            "mY90": f"q{q_no}_mY90",
            "X180C1": f"q{q_no}_X180C1",
            "X180C2": f"q{q_no}_X180C2",
            "X180C3": f"q{q_no}_X180C3",
            "X180C4": f"q{q_no}_X180C4",
            "X180C5": f"q{q_no}_X180C5",
            "X180C6": f"q{q_no}_X180C6",
            "I": "zero",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }


    # add corresponding rr
    config['elements'][f"rr{rr_no}"] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'rr{rr_no}'][0]}", dac_mapping[f'rr{rr_no}'][1][0]),
        #     "Q": (f"con{dac_mapping[f'rr{rr_no}'][0]}", dac_mapping[f'rr{rr_no}'][1][1]),
        #     "lo_frequency": rr_LO[f"{rr_no}"],
        #     "mixer": mixers[f"rr{rr_no}"],
        # },
        "RF_inputs": {"port": (octave, octave_outputs[f"rr{rr_no}"])},
        "RF_outputs": {"port": (octave, octave_inputs[f"rr{rr_no}"])},
        "intermediate_frequency": rr_IF[f"{rr_no}"],
        "outputs": {
            "out1": (f"con{dac_mapping[f'rr{rr_no}'][0]}", 1),
            "out2": (f"con{dac_mapping[f'rr{rr_no}'][0]}", 2),
        },
        "time_of_flight": tof[f"{rr_no}"],
        "smearing": smearing,
        "operations": {
            "const": f"const_pulse",
            "readout": f"q{rr_no}_ro_pulse",
        }
    }

    # if use_octave:
    #     config['elements'][f"q{q_no}"]["RF_inputs"] =  {"port": (octave, octave_outputs[f"q{q_no}"])}
    #     config['elements'][f"rr{rr_no}"]["RF_inputs"] =  {"port": (octave, octave_outputs[f"rr{rr_no}"])},
    #
    #     if use_octave_input:
    #         config['elements'][f"rr{rr_no}"]["RF_outputs"] = {"port": (octave, octave_inputs[f"rr{rr_no}"])},
    #

    ####### ADD CORRESPONDING PULSES #########
    if not "pulses" in config: config["pulses"] = {}
    if not "waveforms" in config: config["waveforms"] = {}
    # add all control pulses
    for key in config["elements"][f"q{q_no}"]["operations"]:
        pul = config["elements"][f"q{q_no}"]["operations"][key]
        # print(pul)
        if pul == "const_pulse" or pul == "zero":
            continue

        if "grft" in pul: #will extract the ""-enclosed strings and use it to knpw what QUA pulse to play(X90/Y90/X180/Y180)
            pul_name = pul.split("_")[1][1:] #q1_Xgrft gives pul_name = grft
        elif "m" in pul:
            pul_name = pul.split('_')[1][1:] #q1_mX90 gives pul_name = X90
        elif "180C1" in pul:
            pul_name = pul.split('_')[1][:4] #q1_X180C1 gives X180
        elif "180C2" in pul:
            pul_name = pul.split('_')[1][:4]
        elif "180C3" in pul:
            pul_name = pul.split('_')[1][:4]
        elif "180C4" in pul:
            pul_name = pul.split('_')[1][:4] #q1_X180C4 gives X180
        elif "180C5" in pul:
            pul_name = pul.split('_')[1][:4]
        elif "180C6" in pul:
            pul_name = pul.split('_')[1][:4]
        elif "90C1" in pul:
            pul_name = pul.split('_')[1][:3] #q1_X90C1 gives X90
        elif "90C2" in pul:
            pul_name = pul.split('_')[1][:3]
        elif "90C3" in pul:
            pul_name = pul.split('_')[1][:3]
        else:
            pul_name = pul.split('_')[1]

        if "180C1" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"]+4*2,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "180C2" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"]+4*4,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "180C3" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"]+4*6,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "180C4" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"]+4*1,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "180C5" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"]+4*2,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "180C6" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"]+4*3,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "90C1" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": piby2_len_ns[f"{q_no}"]+4*1,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "90C2" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": piby2_len_ns[f"{q_no}"]+4*2,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        elif "90C3" in pul:
            config["pulses"][pul] = {
                "operation": "control",
                "length": piby2_len_ns[f"{q_no}"]+4*3,
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }
        else:
            config["pulses"][pul] = {
                "operation": "control",
                "length": pi_len_ns[f"{q_no}"],
                "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
            }

        #START WITH PI PULSES
        if "180" in pul:
            if "X" in pul:
                config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
                # add waveform
                if 'grft' in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}
                elif "m" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [-amp_scale[f"{q_no}"][pul_name]])}
                elif "180C1" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=2)}
                elif "180C2" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=4)}
                elif "180C3" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=6)}
                elif "180C4" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=1)}
                elif "180C5" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=2)}
                elif "180C6" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=3)}
                else:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [amp_scale[f"{q_no}"][pul_name]])}

            if "Y" in pul:
                config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
                # add waveform
                if 'grft' in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}
                elif "m" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [-amp_scale[f"{q_no}"][pul_name]])}
                elif "180C1" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=2)} #8ns
                elif "180C2" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=4)} #16ns
                elif "180C3" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=6)} #24ns
                elif "180C4" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=1)}
                elif "180C5" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=2)}
                elif "180C6" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                                  [amp_scale[f"{q_no}"][pul_name]], n0=3)}
                else:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [amp_scale[f"{q_no}"][pul_name]])}
        #######################
        #NOW DEALING WITH PI/2#
        #######################
        if "90" in pul:
            # config["pulses"][pul]["length"] = piby2_len_ns[f"{q_no}"]
            if "X" in pul:
                config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
                # add waveform
                if 'grft' in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}
                elif "m" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [-amp_scale[f"{q_no}"][pul_name]])}
                elif "90C1" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]], n0=1)}
                elif "90C2" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]], n0=2)}
                elif "90C3" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]], n0=3)}
                else:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]])}

            if "Y" in pul:
                config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
                # add waveform
                if 'grft' in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}
                elif "m" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]])}
                elif "90C1" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]], n0=1)}  # 8ns
                elif "90C2" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]], n0=2)}  # 16ns
                elif "90C3" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_CPMG_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]], n0=3)}  # 24ns
                else:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen(
                                                              (piby2_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                              [amp_scale[f"{q_no}"][pul_name]])}

    # add readout pulse
    config["pulses"][f"q{q_no}_ro_pulse"] = {
        "operation": "measurement",
        "length": ro_len_clk[f"{q_no}"] * 4,
        "waveforms": {"I": f"q{q_no}_ro_wf", "Q": "zero_wf"},
        "integration_weights": {
            "integW_cos": f"integW_cos_rr{q_no}",
            "integW_sin": f"integW_sin_rr{q_no}",
            "integW_minus_sin": f"integW_minus_sin_rr{q_no}"
        },
        "digital_marker": "ON",
    }

    ro_pulse_square = True
    if ro_pulse_square:
        config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "constant",
                                                  "sample": 0.4 * ro_amp[str(rr_no)]}

    else:
        config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "arbitrary",
                                                  "samples": grft_arr_gen((ro_len_clk[str(rr_no)] * 4, 200),
                                                  [ro_amp[str(rr_no)]])}

    # add integration weights
    if not "integration_weights" in config: config["integration_weights"] = {}

    config["integration_weights"][f"integW_cos_rr{rr_no}"] = {}
    config["integration_weights"][f"integW_sin_rr{rr_no}"] = {}
    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"] = {}


    config["integration_weights"][f"integW_cos_rr{rr_no}"]["cosine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_cos_rr{rr_no}"]["sine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    config["integration_weights"][f"integW_sin_rr{rr_no}"]["cosine"] = [
        (np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_sin_rr{rr_no}"]["sine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["cosine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["sine"] = [
        (-np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    # add mixers
    if not "mixers" in config: config["mixers"] = {}
    config["mixers"][f"mixer_q{q_no}"] = [{"intermediate_frequency": q_IF[f"{q_no}"], "lo_frequency": q_LO[f"{q_no}"],
                                           "correction": mixer_corrections[f"q{q_no}"]}]
    config["mixers"][f"mixer_rr{q_no}"] = [
        {"intermediate_frequency": rr_IF[f"{rr_no}"], "lo_frequency": rr_LO[f"{rr_no}"],
         "correction": mixer_corrections[f"rr{rr_no}"]}]

    return config

# ------- DRAG (added by Aneesh) -------

def config_add_drag_elements_q_rr(config, q_no, rr_no, dac_mapping, octave_outputs, octave_inputs,  q_LO, q_IF, q_anh, rr_LO, rr_IF, pi_len_ns, piby2_len_ns, pi_rise_grft_ns, amp_scale,
                                  drag_dict, mixers, mixer_corrections, ro_amp, ro_len_clk, tof, integ_len_clk, optimal_readout_phase, smearing=0, octave="octave1"):
    '''
    Given parameters, this function adds the qubit, readout resonator, and all the standard pulses and waveforms to the config.
    '''

    ################ ADD ELEMENTS ################
    # Add qubit
    if not "elements" in config: config["elements"] = {}
    config['elements'][f"q{q_no}"] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][0]),
        #     "Q": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][1]),
        #     "lo_frequency": q_LO[f"{q_no}"],
        #     "mixer": mixers[f"q{q_no}"],
        # },
        "RF_inputs": {"port": (octave, octave_outputs[f"q{q_no}"])},
        "intermediate_frequency": q_IF[f"{q_no}"],
        "operations": {
            "const": "const_pulse",
            "Xgrft": f"q{q_no}_Xgrft",
            "Ygrft": f"q{q_no}_Ygrft",
            "X180": f"q{q_no}_X180",
            "X90": f"q{q_no}_X90",
            "mX90": f"q{q_no}_mX90",
            "Y180": f"q{q_no}_Y180",
            "Y90": f"q{q_no}_Y90",
            "mY90": f"q{q_no}_mY90",
            # Start of edit
            "d_X180": f"q{q_no}_d_X180",
            "d_X90": f"q{q_no}_d_X90",
            "d_mX90": f"q{q_no}_d_mX90",
            "d_Y180": f"q{q_no}_d_Y180",
            "d_Y90": f"q{q_no}_d_Y90",
            "d_mY90": f"q{q_no}_d_mY90",
            # End of edit
            "I": "zero",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    # add corresponding rr
    config['elements'][f"rr{rr_no}"] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'rr{rr_no}'][0]}", dac_mapping[f'rr{rr_no}'][1][0]),
        #     "Q": (f"con{dac_mapping[f'rr{rr_no}'][0]}", dac_mapping[f'rr{rr_no}'][1][1]),
        #     "lo_frequency": rr_LO[f"{rr_no}"],
        #     "mixer": mixers[f"rr{rr_no}"],
        # },
        "RF_inputs": {"port": (octave, octave_outputs[f"rr{rr_no}"])},
        "RF_outputs": {"port": (octave, octave_inputs[f"rr{rr_no}"])},
        "intermediate_frequency": rr_IF[f"{rr_no}"],
        # "outputs": {
        #     "out1": (f"con{dac_mapping[f'rr{rr_no}'][0]}", 1),
        #     "out2": (f"con{dac_mapping[f'rr{rr_no}'][0]}", 2),
        # },
        "time_of_flight": tof[f"{rr_no}"],
        "smearing": smearing,
        "operations": {
            "const": f"const_pulse",
            "readout": f"q{rr_no}_ro_pulse",
        }
    }

    ####### ADD CORRESPONDING PULSES #########
    if not "pulses" in config: config["pulses"] = {}
    if not "waveforms" in config: config["waveforms"] = {}
    # add all control pulses
    for key in config["elements"][f"q{q_no}"]["operations"]:
        pul = config["elements"][f"q{q_no}"]["operations"][key]
        # print(pul)
        if pul == "const_pulse" or pul == "zero":
            continue

        # Start of edit
        if "grft" in pul:
            pul_name = pul.split("_")[1][1:] #q1_Xgrft
        elif "d" in pul:
            if "m" in pul:
                pul_name = pul.split("_")[2][1:] #q1_d_mX180
            else:
                pul_name = pul.split("_")[2]
        else:
            if "m" in pul:
                pul_name = pul.split("_")[1][1:]
            else:
                pul_name = pul.split("_")[1]
        
        # End of edit

        config["pulses"][pul] = {
            "operation": "control",
            "length": pi_len_ns[f"{q_no}"],
            "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
        }


        if "X" in pul:
            config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
            # add waveform

            # Start of edit

            if "grft" in pul:
                config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}
            elif "d" in pul:
                config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
                if "m" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

                else:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

            else:

                if "m" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [-amp_scale[f"{q_no}"][pul_name]])}
                else:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [amp_scale[f"{q_no}"][pul_name]])}


            # End of edit
            
        if "Y" in pul:
            config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
            # add waveform

            # Start of edit

            if 'grft' in pul:
                config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}
            elif "d" in pul:
                config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
                if "m" in pul:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}

                else:
                    config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=-amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[1]}

                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": drag_grft_pulse_waveforms(
                                                              amplitude=amp_scale[f"{q_no}"][f"{pul_name}"],
                                                              length=pi_len_ns[f"{q_no}"], rise=pi_rise_grft_ns,
                                                              anharmonicity=q_anh[f"{q_no}"],   
                                                              alpha=drag_dict[f"{q_no}"]["alpha"],
                                                              detuning=drag_dict[f"{q_no}"]["det"])[0]}

            else:
                if "m" in pul:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [-amp_scale[f"{q_no}"][pul_name]])}
                else:
                    config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                          "samples": grft_arr_gen((pi_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                    [amp_scale[f"{q_no}"][pul_name]])}
            

            # End of edit

        if "90" in pul:
            config["pulses"][pul]["length"] = piby2_len_ns[f"{q_no}"]

    # add readout pulse
    config["pulses"][f"q{q_no}_ro_pulse"] = {
        "operation": "measurement",
        "length": ro_len_clk[f"{q_no}"] * 4,
        "waveforms": {"I": f"q{q_no}_ro_wf", "Q": "zero_wf"},
        "integration_weights": {
            "integW_cos": f"integW_cos_rr{q_no}",
            "integW_sin": f"integW_sin_rr{q_no}",
            "integW_minus_sin": f"integW_minus_sin_rr{q_no}"
        },
        "digital_marker": "ON",
    }

    ro_pulse_square = False 
    if ro_pulse_square:
        config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "constant",
                                                  "sample": 0.4 * ro_amp[str(rr_no)]}

    else:
        config["waveforms"][f"q{rr_no}_ro_wf"] = {"type": "arbitrary",
                                                  "samples": grft_arr_gen((ro_len_clk[str(rr_no)] * 4, 200),
                                                  [ro_amp[str(rr_no)]])}

    # add integration weights
    if not "integration_weights" in config: config["integration_weights"] = {}

    config["integration_weights"][f"integW_cos_rr{rr_no}"] = {}
    config["integration_weights"][f"integW_sin_rr{rr_no}"] = {}
    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"] = {}


    config["integration_weights"][f"integW_cos_rr{rr_no}"]["cosine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_cos_rr{rr_no}"]["sine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    config["integration_weights"][f"integW_sin_rr{rr_no}"]["cosine"] = [
        (np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_sin_rr{rr_no}"]["sine"] = [
        (np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["cosine"] = [
        (-np.sin(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]
    config["integration_weights"][f"integW_minus_sin_rr{rr_no}"]["sine"] = [
        (-np.cos(optimal_readout_phase[f"rr{rr_no}"]), integ_len_clk[f"{rr_no}"] * 4)]

    # add mixers
    if not "mixers" in config: config["mixers"] = {}
    config["mixers"][f"mixer_q{q_no}"] = [{"intermediate_frequency": q_IF[f"{q_no}"], "lo_frequency": q_LO[f"{q_no}"],
                                           "correction": mixer_corrections[f"q{q_no}"]}]
    config["mixers"][f"mixer_rr{q_no}"] = [
        {"intermediate_frequency": rr_IF[f"{rr_no}"], "lo_frequency": rr_LO[f"{rr_no}"],
         "correction": mixer_corrections[f"rr{rr_no}"]}]

    return config

# ------- End of DRAG (added by Aneesh) -------

def config_add_rise_fall(config, cr_tail_ns):

    config["pulses"]["rise_pulse"] = {
            "operation": "control",
            "length": cr_tail_ns,
            "waveforms": {"I": "rise_wf", "Q": "zero_wf"},
        }

    config["pulses"]["fall_pulse"] = {
        "operation": "control",
        "length": cr_tail_ns,
        "waveforms": {"I": "fall_wf", "Q": "zero_wf"},
    }

    config["waveforms"]["rise_wf"] = {"type": "arbitrary", "samples": rise_arr(cr_tail_ns)}
    config["waveforms"]["fall_wf"] = {"type": "arbitrary", "samples": fall_arr(cr_tail_ns)}

    return config


def config_add_crgate(config, control, target, dac_mapping, q_LO, q_IF, mixers, mixer_corrections, octave, octave_outputs):

    qe = f"cr_c{control}t{target}"
    qe_ac = f"cr_ac_c{control}t{target}"

    config['elements'][qe] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'q{control}'][0]}", dac_mapping[qe][1][0]),
        #     "Q": (f"con{dac_mapping[f'q{control}'][0]}", dac_mapping[qe][1][1]),
        #     "lo_frequency": q_LO[f"{control}"],
        #     "mixer": mixers[qe],
        # },
        "RF_inputs": {"port": (octave, octave_outputs[f"q{control}"])},
        "intermediate_frequency": q_IF[f"{target}"],
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    config['elements'][qe_ac] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'q{target}'][0]}", dac_mapping[f'q{target}'][1][0]),
        #     "Q": (f"con{dac_mapping[f'q{target}'][0]}", dac_mapping[f'q{target}'][1][0]),
        #     "lo_frequency": q_LO[f"{control}"],
        #     "mixer": mixers[f'q{target}'],
        # },
        "RF_inputs": {"port": (octave, octave_outputs[f"q{target}"])},
        "intermediate_frequency": q_IF[f"{target}"],
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    config["mixers"][mixers[qe]] = [{"intermediate_frequency": q_IF[f"{target}"], "lo_frequency": q_LO[f"{control}"], "correction": mixer_corrections[qe]}]

    return config

def config_add_czgate(config, control, target, dac_mapping, q_LO, q_IF, raman_IF,mixers, mixer_corrections, octave, octave_outputs):

    qe = f"cz_c{control}t{target}"
    # qe_ac = f"cr_ac_c{control}t{target}"

    config['elements'][qe] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'q{control}'][0]}", dac_mapping[qe][1][0]),
        #     "Q": (f"con{dac_mapping[f'q{control}'][0]}", dac_mapping[qe][1][1]),
        #     "lo_frequency": q_LO[f"{control}"],
        #     "mixer": mixers[qe],
        # },
         "RF_inputs": {"port": (octave, octave_outputs[f"q{control}"])},
        "intermediate_frequency": raman_IF[f"{control}"],
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    # config['elements'][qe_ac] = {
    #     # "mixInputs": {
    #     #     "I": (f"con{dac_mapping[f'q{target}'][0]}", dac_mapping[f'q{target}'][1][0]),
    #     #     "Q": (f"con{dac_mapping[f'q{target}'][0]}", dac_mapping[f'q{target}'][1][0]),
    #     #     "lo_frequency": q_LO[f"{control}"],
    #     #     "mixer": mixers[f'q{target}'],
    #     # },
    #     "RF_inputs": {"port": (octave, octave_outputs[f"q{target}"])},
    #     "intermediate_frequency": q_IF[f"{target}"],
    #     "operations": {
    #         "const": "const_pulse",
    #         "rise": "rise_pulse",
    #         "fall": "fall_pulse",
    #     },
    # }

    # config["mixers"][mixers[qe]] = [{"intermediate_frequency": cz_IF[f"{control}"], "lo_frequency": q_LO[f"{control}"]}]

    return config

def config_add_q12(config, q_no, dac_mapping, octave_outputs, q_LO, q12_IF,q12_LO,
                   pi_12_len_ns, piby2_12_len_ns, pi_rise_grft_ns, amp_12_scale, mixers, mixer_corrections, use_octave=True, octave="octave1"):


    config['elements'][f"q12_{q_no}"] = {
        # "mixInputs": {
        #     "I": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][0]),
        #     "Q": (f"con{dac_mapping[f'q{q_no}'][0]}", dac_mapping[f'q{q_no}'][1][1]),
        #     "lo_frequency": q_LO[f"{q_no}"],
        #     "mixer": mixers[f"q12_{q_no}"],
        # },
        "RF_inputs": {"port": (octave, octave_outputs[f"q{q_no}"])},
        "intermediate_frequency": q12_IF[f"{q_no}"],
        "operations": {
            "const": "const_pulse",
            "grft": f"q12_{q_no}_grft",
            "X180": f"q12_{q_no}_X180",
            "X90": f"q12_{q_no}_X90",
            "mX90": f"q12_{q_no}_mX90",
            "Y180": f"q12_{q_no}_Y180",
            "Y90": f"q12_{q_no}_Y90",
            "mY90": f"q12_{q_no}_mY90",
            "I": "zero",
        },
    }

    # if use_octave:
    #     config['elements'][f"q12_{q_no}"]["RF_inputs"] = {"port": (octave, octave_outputs[f"q{q_no}"])},

    for key in config["elements"][f"q12_{q_no}"]["operations"]:
        pul = config["elements"][f"q12_{q_no}"]["operations"][key]
        # print(pul)
        if pul == "const_pulse" or pul == "zero":
            continue

        pul_name = pul.split('_')[2]
        if "m" in pul: pul_name = pul.split('_')[2][1:]


        config["pulses"][pul] = {
            "operation": "control",
            "length": pi_12_len_ns[f"{q_no}"],
            "waveforms": {"I": "zero_wf", "Q": "zero_wf"},
        }

        if 'grft' in pul:
            config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
            config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                  "samples": grft_arr_gen((pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns), 1)}

        if "X" in pul:
            config["pulses"][pul]["waveforms"]["I"] = f"{pul}_I_wf"
            # add waveform
            if "m" in pul:
                config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                [-amp_12_scale[f"{q_no}"][pul_name]])}
            else:
                config["waveforms"][f"{pul}_I_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                [amp_12_scale[f"{q_no}"][pul_name]])}

        if "Y" in pul:
            config["pulses"][pul]["waveforms"]["Q"] = f"{pul}_Q_wf"
            # add waveform
            if "m" in pul:
                config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                [-amp_12_scale[f"{q_no}"][pul_name]])}
            else:
                config["waveforms"][f"{pul}_Q_wf"] = {"type": "arbitrary",
                                                      "samples": grft_arr_gen((pi_12_len_ns[f"{q_no}"], pi_rise_grft_ns),
                                                                [amp_12_scale[f"{q_no}"][pul_name]])}

        if "90" in pul:
            config["pulses"][pul]["length"] = piby2_12_len_ns[f"{q_no}"]

        # if q_no == 4:
        #     config["mixers"][f"mixer_q12_{q_no}"] = [
        #         {"intermediate_frequency": q12_IF[f"{q_no}"], "lo_frequency": q12_LO[f"{q_no}"],
        #          "correction": mixer_corrections[f"q12_{q_no}"]}]

    return config

def config_add_sizzle(config, target, dac_mapping,  siz_IF,mixers, mixer_corrections, octave, octave_outputs):

    qe = f"siz_{target}"

    config['elements'][qe] = {
         "RF_inputs": {"port": (octave, octave_outputs[f"q{target}"])},
        "intermediate_frequency": siz_IF[f"{target}"],
        "sticky": {"analog" : True, "duration" : 4},
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    return config

def config_add_cz_sizzle(config, target, dac_mapping,  cz_IF,mixers, mixer_corrections, octave, octave_outputs):

    qe = f"cz_{target}"

    config['elements'][qe] = {
         "RF_inputs": {"port": (octave, octave_outputs[f"q{target}"])},
        "intermediate_frequency": cz_IF[f"{target}"],
        "sticky": {"analog" : True, "duration" : 4},
        "operations": {
            "const": "const_pulse",
            "rise": "rise_pulse",
            "fall": "fall_pulse",
        },
    }

    return config
