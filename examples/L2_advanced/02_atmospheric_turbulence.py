# Atmospheric turbulence demo
import matplotlib; matplotlib.use("Agg")
import sys; sys.path.insert(0, ".")
import numpy as np
import matplotlib.pyplot as plt
from src.sources.beam import gaussian_beam
from src.propagators.bpm import angular_spectrum_propagate
from src.media.atmosphere import kolmogorov_phase_screen, apply_phase
wvl = 633e-9; w0 = 0.5e-3; r0 = 0.2; z_total = 1.0
x = np.linspace(-3e-3, 3e-3, 256); dx = x[1] - x[0]
X, Y = np.meshgrid(x, x)
E0 = gaussian_beam(X, Y, w0)
E = E0.copy(); n_steps = 20; dz = z_total / n_steps
z_vals = []; fields = []
for i in range(n_steps):
    E = angular_spectrum_propagate(E, X, Y, wvl, dz)
    phase = kolmogorov_phase_screen(256, dx, r0)
    E = apply_phase(E, phase)
    if i % 5 == 0 or i == n_steps - 1:
        z_vals.append((i+1)*dz); fields.append(E.copy())
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for i in range(min(4, len(fields))):
    z = z_vals[i]; f = fields[i]
    I = np.abs(f)**2
    axes[i].imshow(I, extent=[x[0]*1e3, x[-1]*1e3]*2, cmap="inferno")
    axes[i].set_title(f"z={z*1e3:.0f} mm"); axes[i].axis("off")
plt.tight_layout(); plt.savefig("L2_turbulence.png", dpi=150)
print("Saved L2_turbulence.png")
plt.close()
# Also show the phase screen
phase = kolmogorov_phase_screen(256, dx, r0)
plt.figure(figsize=(6,5))
plt.imshow(phase, cmap="RdBu", extent=[x[0]*1e3, x[-1]*1e3]*2)
plt.colorbar(label="Phase (rad)"); plt.title("Kolmogorov Phase Screen")
plt.xlabel("x (mm)"); plt.ylabel("y (mm)")
plt.tight_layout(); plt.savefig("L2_phase_screen.png", dpi=150)
print("Saved L2_phase_screen.png")
