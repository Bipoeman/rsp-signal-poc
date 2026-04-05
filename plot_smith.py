import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
import csv

def plot_smith_with_skrf(frequencies, impedances, title="Smith Chart"):
    """
    Plot impedance data on a Smith chart using scikit-rf.

    Parameters:
    frequencies: array-like, frequencies in Hz
    impedances: array-like, complex impedances Z = R + jX
    title: str, plot title
    """
    # Create a Network object from impedance data
    # scikit-rf expects S-parameters, so we need to convert impedance to S11
    Z0 = 50.0  # Characteristic impedance
    s11 = (impedances - Z0) / (impedances + Z0)  # Reflection coefficient

    # Create frequency object
    freq = rf.Frequency.from_f(frequencies, unit='Hz')

    # Create Network with S11 data
    # S-parameters are stored as [frequency, 2, 2] array for 2-port network
    s = np.zeros((len(frequencies), 2, 2), dtype=complex)
    s[:, 0, 0] = s11  # S11
    s[:, 1, 1] = s11  # S22 (assuming reciprocal)
    s[:, 0, 1] = np.zeros(len(frequencies))  # S12
    s[:, 1, 0] = np.zeros(len(frequencies))  # S21

    network = rf.Network(frequency=freq, s=s, name='Impedance Data')

    # Plot Smith chart
    fig, ax = plt.subplots(figsize=(8, 8))
    network.plot_s_smith(ax=ax, show_legend=True)
    ax.set_title(title)

    return fig, ax

def load_impedance_data(filename):
    """
    Load impedance data from CSV file.
    Expected format: frequency, real_part, imag_part
    or: frequency, magnitude, phase_degrees
    """
    frequencies = []
    impedances = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        header = next(reader, None)  # Read header

        for row in reader:
            if len(row) >= 3:
                freq = float(row[0])

                if len(row) == 3:  # frequency, real, imag
                    real = float(row[1])
                    imag = float(row[2])
                    impedances.append(complex(real, imag))
                elif len(row) == 4:  # frequency, mag, phase, something
                    mag = float(row[1])
                    phase_deg = float(row[2])
                    phase_rad = np.deg2rad(phase_deg)
                    impedances.append(mag * np.exp(1j * phase_rad))

                frequencies.append(freq)

    return np.array(frequencies), np.array(impedances)

def load_transfer_function_data(filename):
    """
    Load transfer function data (gain, phase) and convert to impedance if possible.
    This is a simplified conversion - for accurate results, proper measurement setup is needed.

    Expected format: frequency, gain, phase_degrees
    """
    frequencies = []
    gains = []
    phases = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header

        for row in reader:
            if len(row) >= 3:
                freq = float(row[0])
                gain = float(row[1])
                phase_deg = float(row[2])
                frequencies.append(freq)
                gains.append(gain)
                phases.append(phase_deg)

    # Convert to complex transfer function
    H = np.array(gains) * np.exp(1j * np.deg2rad(phases))

    # For demonstration, assume this is S21 and try to estimate S11
    # This is NOT accurate for real measurements - you need proper VNA setup
    # Here we just plot the transfer function magnitude on a polar plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(np.deg2rad(phases), 20 * np.log10(gains))
    ax.set_title('Transfer Function (Polar Plot)')
    ax.set_rlabel_position(90)
    ax.grid(True)

    return fig, ax

# Example usage
if __name__ == "__main__":
    print("Smith Chart Plotting Script")
    print("===========================")
    print()
    print("This script can plot impedance data on a Smith chart.")
    print("Your current data appears to be transfer function measurements (gain, phase).")
    print()
    print("For Smith chart plotting, you need complex impedance data: Z = R + jX")
    print("or reflection coefficient data: Γ = |Γ|∠θ")
    print()
    print("To use this script:")
    print("1. Prepare your data in CSV format:")
    print("   - For impedance: frequency, real(Z), imag(Z)")
    print("   - For reflection: frequency, |Γ|, ∠Γ (degrees)")
    print()
    print("2. Call: frequencies, impedances = load_impedance_data('your_file.csv')")
    print("3. Call: plot_smith_with_skrf(frequencies, impedances)")
    print()
    print("Example with sample RC filter data:")

    # Create sample impedance data for demonstration
    frequencies = np.logspace(1, 6, 50)  # 10 Hz to 1 MHz
    R = 1000  # ohms
    C = 1e-6  # farads
    impedances = np.array([1 / (1/R + 1j * 2 * np.pi * f * C) for f in frequencies])

    try:
        fig, ax = plot_smith_with_skrf(frequencies, impedances, "Sample RC Filter Smith Chart")
        plt.show()
    except ImportError:
        print("scikit-rf not available. Install with: pip install scikit-rf")
        print("Falling back to basic matplotlib implementation...")

        # Fallback to basic implementation
        plot_smith_chart(frequencies, impedances, "Sample RC Filter Smith Chart")

    print()
    print("To plot your actual data, modify the script calls above.")