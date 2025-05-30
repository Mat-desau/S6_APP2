import numpy as np
import subprocess
from ltspice import Ltspice
import os

# Path to LTspice on macOS
LTSPICE_PATH = "/Applications/LTspice.app/Contents/MacOS/LTspice"

# Resistor sweep values
Rz1_values = np.linspace(1e3, 1e6, 10)  # 1k to 1M
Rd_values = np.linspace(1e3, 20e3, 10)  # 1k to 20k

best_score = -np.inf
best_config = None

for Rz1 in Rz1_values:
    for Rd in Rd_values:
        # Generate netlist
        with open("/Users/francoisdesautels/Documents/GitHub/S6_APP2/APP/Tests/Etage1.net", "r") as f:
            netlist = f.read()
        netlist = netlist.replace("{{RZ1}}", f"{Rz1}")
        netlist = netlist.replace("{{RD}}", f"{Rd}")

        with open("/Users/francoisdesautels/Documents/GitHub/S6_APP2/APP/Tests/diff_amp_run.cir", "w") as f:
            f.write(netlist)

        # Run LTspice simulation
        subprocess.run([LTSPICE_PATH, "-b", "/Users/francoisdesautels/Documents/GitHub/S6_APP2/APP/Tests/diff_amp_run.cir"])

        # Read and parse .raw output
        l = Ltspice("/Users/francoisdesautels/Documents/GitHub/S6_APP2/APP/Tests/Etage1.raw")
        l.parse()

        try:
            vo1 = l.get_data("vo1")
            time = l.get_time()
        except KeyError:
            print(f"Vo1 not found for Rz1={Rz1}, Rd={Rd}")
            continue

        # Compute peak-to-peak voltage as performance score
        p2p = np.max(vo1) - np.min(vo1)

        if p2p > best_score:
            best_score = p2p
            best_config = (Rz1, Rd)

print("\nBest configuration found:")
print(f"Rz1 = {best_config[0]:.1f} Ω")
print(f"Rd  = {best_config[1]:.1f} Ω")
print(f"Peak-to-peak Vo1 = {best_score:.2f} V")
