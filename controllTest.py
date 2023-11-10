import pyvisa
import time
rm = pyvisa.ResourceManager()
print(rm.list_resources())
# function_gen = rm.open_resource('USB0::0x049F::0x505B::CN2025006001104::0::INSTR')
# scope = rm.open_resource('TCPIP0::192.168.28.18::inst0::INSTR')

# # function_gen.write("OUTPut1 ON")
# function_gen.write(f'SOURce1:FREQ 5000')
