import pyvisa
import time
rm = pyvisa.ResourceManager()
print(rm.list_resources())
function_gen = rm.open_resource('USB0::0x049F::0x505B::CN2025006001104::0::INSTR')
# scope = rm.open_resource('TCPIP0::192.168.28.18::inst0::INSTR')
scope = rm.open_resource('USB0::0xF4EC::0xEE38::SDSMMEBC3R1349::0::INSTR')
import matplotlib.pyplot as plt

import numpy as np

def cal_freq_range(freq_min,freq_max,num_point):
    logStart = np.log10(freq_min)
    logEnd = np.log10(freq_max)
    # interval = (logEnd - logStart) / (num_point - 1)
    log_freq = np.linspace(logStart,logEnd,num_point)
    freq_ret = 10 ** log_freq
    # freq_i = []
    # for i in range(num_point):
    #     freq_i.append(float(f"{10**(2+i*interval):.2f}"))
    # print(freq_i)
    return freq_ret

def float_pava_pkpk(msg : str):
    return float(msg.split(",")[1].split("V")[0])

def float_pava_freq(msg : str):
    return float(msg.split(",")[1].split("Hz")[0])

def float_vdiv(msg : str):
    return float(msg.split(" ")[1].split("V")[0])

def float_tdiv(msg : str):
    return float(msg.split(" ")[1].split("S")[0])

def right_vdiv_for_pkpk(channel : str):
    
    lenArr = 12
    
    v_val = scope.query(f"{channel}:PAVA? PKPK")
    v_val = float_pava_pkpk(v_val)
    v_div = scope.query(f"{channel}:VDIV?")
    v_div = float_vdiv(v_div)
    
    num_grid_vert = 4 * 2
    v_div_num = [10e-3,20e-3,50e-3]
    # v_div_num = [10e-2,20e-2,50e-2]
    v_div_available : list = [v_div_num[i % 3] * 10**((i)//3) for i in range(lenArr)]
    v_div_index = v_div_available.index(v_div)
    # for i in range(12):
        
    print(v_div_available)
    print("v_val : ",v_val)
    print(v_div * num_grid_vert)
    if (v_val > v_div * num_grid_vert * 0.9):
        print("It's over scale")
        for i in range(v_div_index,12):
            pkpk = scope.query(f"{channel}:PAVA? PKPK")
            pkpk = float_pava_pkpk(pkpk)
            vdiv = scope.query(f"{channel}:VDIV?")
            vdiv = float_vdiv(vdiv)
            print(f"index : {i}, pkpk : {pkpk} , max : {vdiv * num_grid_vert}")
            if (pkpk > vdiv * num_grid_vert * 0.9):
                scope.write(f"{channel}:VDIV {v_div_available[i]}")
            else:
                break
    if (v_val < v_div * 2.5):
        print("It's under scale")
        for i in reversed(range(lenArr)):
            pkpk = scope.query(f"{channel}:PAVA? PKPK")
            pkpk = float_pava_pkpk(pkpk)
            vdiv = scope.query(f"{channel}:VDIV?")
            vdiv = float_vdiv(vdiv)
            print(f"index : {i}, pkpk : {pkpk} , max : {vdiv * num_grid_vert}")
            if (pkpk < vdiv * 2.5):
                scope.write(f"{channel}:VDIV {v_div_available[i]}")
            else:
                break
            
def right_time_div(channel : str):
    num_grid_hori = 7
    time_div_num = [1e-9,2e-9,5e-9]
    time_div_available : list = [float(f"{time_div_num[i % 3] * 10**((i)//3):.9f}") for i in range(32)]
    time_div = float_tdiv(scope.query(f"TDIV?"))
    print(time_div_available)
    time_div_index = time_div_available.index(time_div)
    for i in range(time_div_index,len(time_div_available)):
        freq = scope.query(f"{channel}:PAVA? FREQ")
        print(f"queried : {freq}")
        time_div = float_tdiv(scope.query(f"TDIV?"))
        time_div_index = time_div_available.index(time_div)
        try:
            freq = float_pava_freq(freq)
        except Exception as e:
            print(e)
            scope.write(f"TDIV {time_div_available[time_div_index+1]}")
            continue
        T = 1/freq
        for i in time_div_available:
            if T < i * num_grid_hori and T > i * (num_grid_hori/2):
                scope.write(f"TDIV {i}")
                break   
        break
    print(freq)
    print(time_div)
    
def right_time_div_ext_freq(channel : str,freq : float):
    num_grid_hori = 7
    time_div_num = [1e-9,2e-9,5e-9]
    time_div_available : list = [float(f"{time_div_num[i % 3] * 10**((i)//3):.9f}") for i in range(32)]
    time_div = float_tdiv(scope.query(f"TDIV?"))
    print(time_div_available)
    T = 1/freq
    for i in time_div_available:
        if T < i * num_grid_hori and T > i * (num_grid_hori/2):
            scope.write(f"TDIV {i}")
            break   
    print(freq)
    print(time_div)



# scope.write(f"{channel}:VDIV {v_div_available[i]}")
                
        

# print(vpk)
# freq = 1700
freqArr = cal_freq_range(20,20000,100)
inArr = []
outArr = []
fileName = '100_Q0.5'
with open(f'./EasyEQ test results/{fileName}.csv', 'w') as f:
    f.write('')

# print(freqArr)


for freq in freqArr:
    function_gen.write(f'SOURce1:FREQ {freq}')
    
    # right_time_div("C1")
    right_time_div_ext_freq("C1",freq)
    right_vdiv_for_pkpk("C1")
    right_vdiv_for_pkpk("C2")
    time.sleep(0.2)
    vin = float_pava_pkpk(scope.query("C1:PAVA? PKPK"))
    vout = float_pava_pkpk(scope.query("C2:PAVA? PKPK"))
    # inArr.append()
    # outArr.append()
    print(f'{freq},{vout/vin}',file=open(f'./EasyEQ test results/{fileName}.csv', 'a'))

# function_gen.write(f'SOURce1:FREQ {freq}')
# for j in range(4):
#     for i in range(9):
#         try:
#             freq = (i + 1) * (10 ** j)
#             function_gen.write(f'SOURce1:FREQ {freq}')
#             sumvpk = 0
#             sumvin = 0
#             vpk = 0
#             vin = 0
#             for i in range(10):
#                 vpk : str = scope.query("C1:PAVA? PKPK")
#                 vin : str = scope.query("C2:PAVA? PKPK")
#                 print(vpk,vin)
#                 vpk : int = float(vpk.split(',')[1].split('V')[0])
#                 vin : int = float(vin.split(',')[1].split('V')[0])
#                 sumvin += vin
#                 sumvpk += vpk
#                 time.sleep(0.2) 
#             sumvin = sumvin / 10
#             sumvpk = sumvpk / 10
#             # inArr.append(sumvin)
#             # outArr.append(sumvpk)
#             # freqArr.append(freq)
#             # print(f'Frequency : {(i + 1) * 100} Ratio : {vpk/vin}')
#             print(f'{freq},{sumvpk/sumvin}',file=open('inout.csv', 'a'))
#         except Exception as e:
#             print(e)
#         time.sleep(0.05)
# plt.plot(freq,inArr)
# print(scope.query('*IDN?'))
