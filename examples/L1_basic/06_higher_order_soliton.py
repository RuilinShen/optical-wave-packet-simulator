# Experiment: Higher-Order Soliton (N=2)
import sys
sys.path.insert(0, ".")
import numpy as np
from src.core import time_grid, freq_grid
from src.sources import gaussian_pulse
from src.propagators import ssfm_propagate
from src.observables import plot_evolution
T0 = 1.0
beta2 = -20.0
gamma = 2.0
N = 2
length = 30.0
dz = 0.01
NT = 2**12
Tmax = 20.0
t, dt = time_grid(NT, Tmax)
w, _ = freq_grid(NT, dt)
A0 = gaussian_pulse(t, T0)
P0 = N**2 * abs(beta2) / (gamma * T0**2)
A0 = A0 * np.sqrt(P0)
result = ssfm_propagate(A0, t, w, beta2, gamma, length, dz)
print(f"N={N} soliton, P0={P0:.1f} W, distance={length} km")
plot_evolution(result, t, w, save_path="06_higher_order_soliton.png")
