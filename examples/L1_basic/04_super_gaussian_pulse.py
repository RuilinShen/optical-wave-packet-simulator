# Experiment 1.4: Super-Gaussian pulse propagation
import sys
sys.path.insert(0, ".")
import numpy as np
from src.core import time_grid, freq_grid
from src.sources import gaussian_pulse, super_gaussian
from src.propagators import ssfm_propagate_dispersion_only
from src.observables import plot_evolution
T0 = 1.0
m = 3
beta2 = -20.0
length = 5.0
dz = 0.01
NT = 2**12
Tmax = 20.0
t, dt = time_grid(NT, Tmax)
w, _ = freq_grid(NT, dt)
A_sg = super_gaussian(t, T0, m)
result_sg = ssfm_propagate_dispersion_only(A_sg, t, w, beta2, length, dz)
print(f"Super-Gaussian order m={m}, distance={length} km")
plot_evolution(result_sg, t, w, save_path="04_super_gaussian_pulse.png")
