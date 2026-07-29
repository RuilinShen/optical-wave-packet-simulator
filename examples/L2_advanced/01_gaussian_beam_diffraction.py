# Gaussian beam diffraction demo
import matplotlib
matplotlib.use("Agg")
import sys; sys.path.insert(0, ".")
import numpy as np
import matplotlib.pyplot as plt
from src.sources.beam import gaussian_beam
from src.propagators.bpm import beam_propagate
wvl = 633e-9; w0 = 0.5e-3; z_max = 2.0
x = np.linspace(-3e-3, 3e-3, 256)
X, Y = np.meshgrid(x, x)
E0 = gaussian_beam(X, Y, w0)
res = beam_propagate(E0, X, Y, wvl, z_max, 30)
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for idx, zi in enumerate([0, 9, 19, 29]):
    r, c = divmod(idx, 2)
    I = np.abs(res["fields"][zi]) ** 2
    axes[r, c].imshow(I, extent=[x[0]*1e3, x[-1]*1e3]*2, cmap="inferno")
    axes[r, c].set_title(f"z={res['z'][zi]*1e3:.0f} mm")
    axes[r, c].set_xlabel("x (mm)"); axes[r, c].set_ylabel("y (mm)")
plt.tight_layout(); plt.savefig("L2_gaussian_beam.png", dpi=150)
print("Saved L2_gaussian_beam.png")
