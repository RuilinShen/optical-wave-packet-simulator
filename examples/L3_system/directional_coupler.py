"""定向耦合器模拟 demo — 对称平板波导倏逝波耦合。
"""
import sys; sys.path.insert(0, ".")
import numpy as np
import matplotlib.pyplot as plt
from src.media.waveguide import coupling_coefficient, coupled_power, dual_waveguide_profile

# 波导参数
wvl = 633e-9; n_core = 1.55; n_clad = 1.45
w = 0.5e-6; gap = 0.5e-6; L = 0.003

kappa = coupling_coefficient(wvl, n_core, n_clad, w, gap)
L_c = np.pi / (2 * kappa)
print(f"kappa = {kappa:.1f} /m")
print(f"耦合长度 Lc = {L_c*1e3:.3f} mm")

z, P1, P2 = coupled_power(kappa, L, 500)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(z*1e3, P1, label="Waveguide 1", lw=2)
ax1.plot(z*1e3, P2, label="Waveguide 2", lw=2)
ax1.axvline(L_c*1e3, color="gray", ls="--", alpha=0.5, label=f"L_c={L_c*1e3:.2f}mm")
ax1.set_xlabel("z (mm)"); ax1.set_ylabel("Power")
ax1.set_title("Power Transfer"); ax1.legend(); ax1.grid(alpha=0.3)

x = np.linspace(-3e-6, 3e-6, 1000)
n = dual_waveguide_profile(x, w, gap, n_core, n_clad)
ax2.plot(x*1e6, n, "b-", lw=2)
ax2.set_xlabel("x (um)"); ax2.set_ylabel("n")
ax2.set_title("Cross-Section"); ax2.grid(alpha=0.3)

plt.tight_layout()
out = "examples/L3_system/directional_coupler_demo.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved: {out}")
