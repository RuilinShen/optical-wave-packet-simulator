# Experiment: Third-Order Dispersion (TOD)
import sys
sys.path.insert(0, ".")
import numpy as np
from src.core import time_grid, freq_grid
from src.sources import gaussian_pulse
from src.propagators import ssfm_propagate_dispersion_only
from src.observables import plot_evolution
T0 = 1.0
beta2 = -20.0
beta3 = 1.0
length = 10.0
dz = 0.01
NT = 2**12
Tmax = 20.0
t, dt = time_grid(NT, Tmax)
w, _ = freq_grid(NT, dt)
A0 = gaussian_pulse(t, T0)
result = ssfm_propagate_dispersion_only(A0, t, w, beta2, length, dz, beta3)
print(f"TOD effect: beta3={beta3}, distance={length} km")
plot_evolution(result, t, w, save_path="05_tod_effect.png")
