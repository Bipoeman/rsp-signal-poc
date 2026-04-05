import pyvisa
import time
import matplotlib.pyplot as plt
import numpy as np
import csv
import instrumentData
import instrument_interface

import usbtmc   

rm = pyvisa.ResourceManager()
print("\033[32mAvailable resources:\033[0m", rm.list_resources())
print("\033[32mUSB TMC Found:  \033[0m", usbtmc.list_devices())
function_gen, scope = instrument_interface.connect_instruments()

def cal_freq_range(freq_min, freq_max, num_point):
    logStart = np.log10(freq_min)
    logEnd = np.log10(freq_max)
    log_freq = np.linspace(logStart, logEnd, num_point)
    freq_ret = 10 ** log_freq
    return freq_ret

def right_vdiv_for_pkpk(channel: str):
    lenArr = 12
    v_val = instrument_interface.get_pkpk(scope, channel)
    v_div = instrument_interface.get_vdiv(scope, channel)
    num_grid_vert = 4 * 2
    v_div_num = [10e-3, 20e-3, 50e-3]
    v_div_available: list = [v_div_num[i % 3] * 10**((i)//3) for i in range(lenArr)]
    v_div_index = v_div_available.index(v_div)
    if (v_val > v_div * num_grid_vert * 0.9):
        for i in range(v_div_index, 12):
            pkpk = instrument_interface.get_pkpk(scope, channel)
            vdiv = instrument_interface.get_vdiv(scope, channel)
            if (pkpk > vdiv * num_grid_vert * 0.9):
                instrument_interface.set_vdiv(scope, channel, v_div_available[i])
            else:
                break
    if (v_val < v_div * 2.5):
        print("It's under scale")
        for i in reversed(range(lenArr)):
            pkpk = instrument_interface.get_pkpk(scope, channel)
            vdiv = instrument_interface.get_vdiv(scope, channel)
            if (pkpk < vdiv * 2.5):
                instrument_interface.set_vdiv(scope, channel, v_div_available[i])
            else:
                break

def right_time_div(channel: str):
    num_grid_hori = 7
    time_div_num = [1e-9, 2e-9, 5e-9]
    time_div_available: list = [float(f"{time_div_num[i % 3] * 10**((i)//3):.9f}") for i in range(32)]
    time_div = instrument_interface.get_tdiv(scope)
    print(time_div_available)
    time_div_index = time_div_available.index(time_div)
    for i in range(time_div_index, len(time_div_available)):
        freq = instrument_interface.get_freq(scope, channel)
        print(f"queried : {freq}")
        time_div = instrument_interface.get_tdiv(scope)
        time_div_index = time_div_available.index(time_div)
        try:
            freq_val = freq
        except Exception as e:
            print(e)
            instrument_interface.set_tdiv(scope, time_div_available[time_div_index+1])
            continue
        T = 1/freq_val
        for i in time_div_available:
            if T < i * num_grid_hori and T > i * (num_grid_hori/2):
                instrument_interface.set_tdiv(scope, i)
                break
        break

def right_time_div_ext_freq(channel: str, freq: float):
    num_grid_hori = 7
    time_div_num = [1e-9, 2e-9, 5e-9]
    time_div_available: list = [float(f"{time_div_num[i % 3] * 10**((i)//3):.9f}") for i in range(32)]
    time_div = instrument_interface.get_tdiv(scope)
    T = 1/freq
    for i in time_div_available:
        if T < i * num_grid_hori and T > i * (num_grid_hori/2):
            instrument_interface.set_tdiv(scope, i)
            break

###################### Buzzer Off before measurement ######################
## BUZZ ON / OFF

freqArr = cal_freq_range(1000, 10000, 200)
fileName = 'lrFilter1'

with open(f'./EasyEQ test results/{fileName}.csv', 'w') as f:
    f.write('Frequency,Gain,Phase\n')

for freq in freqArr:
    instrument_interface.set_frequency(function_gen, freq)
    print(f"Frequency : {freq}", end="... ")
    right_time_div_ext_freq("C1", freq)
    right_vdiv_for_pkpk("C1")
    right_vdiv_for_pkpk("C2")
    print(np.exp(freq * -0.05), end=" ")
    time.sleep(np.exp(freq * -0.05))
    vin = instrument_interface.get_pkpk(scope, "C1")
    vout = instrument_interface.get_pkpk(scope, "C2")
    phase = instrument_interface.get_phase(scope)
    print(f'{freq},{vout/vin},{phase}', file=open(f'./EasyEQ test results/{fileName}.csv', 'a'))
    print("Done")

# Plotting
freq = []
mag = []
phase = []
with open(f'./EasyEQ test results/{fileName}.csv', 'r') as file:
    print("File opened")
    reader = csv.reader(file)
    for row in reader:
        if not row:
            continue
        try:
            freq_val = float(row[0])
            mag_val = 20 * np.log10(float(row[1]))
            phase_val = float(row[2])
        except ValueError:
            continue
        freq.append(freq_val)
        mag.append(mag_val)
        phase.append(phase_val)

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))
ax1.set_xscale("log")
ax1.plot(freq, mag, marker='o', linestyle='-')
ax1.set_ylabel("Gain (dB)")
ax1.set_title("EasyEQ Frequency Response")
ax1.grid(True, which="both", ls="-")

ax2.set_xscale("log")
ax2.plot(freq, phase, marker='o', linestyle='-', color='tab:orange')
ax2.set_ylabel("Phase")
ax2.set_xlabel("Frequency (Hz)")
ax2.grid(True, which="both", ls="-")

fig.tight_layout()
fig.savefig(f"./EasyEQ test results/{fileName}.svg")
fig.savefig(f"./EasyEQ test results/{fileName}.png")
plt.show()