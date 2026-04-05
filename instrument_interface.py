import pyvisa
import time
import instrumentData

rm = pyvisa.ResourceManager('@py')



def connect_instruments():
    """Connect to function generator and oscilloscope."""
    function_gen = rm.open_resource(instrumentData.function_gen_id)
    scope = rm.open_resource(instrumentData.scope_id)
    scope.timeout = 5000  # Set timeout for scope queries
    function_gen.timeout = 5000  # Set timeout for function generator queries
    return function_gen, scope

def set_frequency(function_gen, freq):
    """Set the frequency on the function generator."""
    function_gen.write(f'SOURce1:FREQ {freq}')

def query_scope(scope, command):
    """Send a query to the oscilloscope."""
    return scope.query(command)

def write_scope(scope, command):
    """Send a write command to the oscilloscope."""
    scope.write(command)

def write_function_gen(function_gen, command):
    """Send a write command to the function generator."""
    function_gen.write(command)

# Parsing functions
def float_pava_pkpk(msg: str):
    return float(msg.split(",")[1].split("V")[0])

def float_pava_freq(msg: str):
    return float(msg.split(",")[1].split("Hz")[0])

def float_vdiv(msg: str):
    return float(msg.split(" ")[1].split("V")[0])

def float_tdiv(msg: str):
    return float(msg.split(" ")[1].split("S")[0])

def float_phase(msg: str):
    return float(msg.split(",")[1].split("degree")[0])

# Low-level measurement functions
def get_pkpk(scope, channel):
    """Get peak-to-peak voltage for a channel."""
    msg = query_scope(scope, f"{channel}:PAVA? PKPK")
    return float_pava_pkpk(msg)

def get_vdiv(scope, channel):
    """Get vertical division for a channel."""
    msg = query_scope(scope, f"{channel}:VDIV?")
    return float_vdiv(msg)

def set_vdiv(scope, channel, vdiv):
    """Set vertical division for a channel."""
    write_scope(scope, f"{channel}:VDIV {vdiv}")

def get_tdiv(scope):
    """Get time division."""
    msg = query_scope(scope, "TDIV?")
    return float_tdiv(msg)

def set_tdiv(scope, tdiv):
    """Set time division."""
    write_scope(scope, f"TDIV {tdiv}")

def get_freq(scope, channel):
    """Get frequency measurement for a channel."""
    msg = query_scope(scope, f"{channel}:PAVA? FREQ")
    return float_pava_freq(msg)

def get_phase(scope):
    """Get phase difference between C1 and C2."""
    for i in range(32):
        try:
            msg = query_scope(scope, "C1-C2:MEAD? PHA")
            phase_val = float_phase(msg)
            return phase_val
        except Exception as e:
            print(f"Error occurred while querying phase: {e}")
            continue
    # return float_phase(msg)