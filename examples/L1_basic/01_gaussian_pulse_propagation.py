"""
实验 1.1：高斯脉冲在色散光纤中的传播
物理：群速度色散 (GVD) 导致脉冲展宽
方法：对称分步傅里叶法 (SSFM)，纯色散（无非线性）
"""

import sys
sys.path.insert(0, ".")

from src.core import time_grid, freq_grid
from src.sources import gaussian_pulse
from src.propagators import ssfm_propagate_dispersion_only
from src.observables import plot_evolution

# ── 参数 ────────────────────────────────────────────
T0 = 1.0          # 脉冲宽度 [ps]
beta2 = -20.0     # GVD [ps^2/km]（反常色散）
length = 5.0      # 传播距离 [km]
dz = 0.01         # 步长 [km]
NT = 2**12        # 采样点数
Tmax = 20.0       # 时间窗口 [ps]

# ── 网格 ────────────────────────────────────────────
t, dt = time_grid(NT, Tmax)
w, _ = freq_grid(NT, dt)

# ── 初始脉冲 ────────────────────────────────────────
A0 = gaussian_pulse(t, T0)

# ── 传播 ────────────────────────────────────────────
result = ssfm_propagate_dispersion_only(
    A0, t, w, beta2, length, dz
)

print(f"初始脉冲宽度: {T0:.2f} ps")
print(f"最终脉冲宽度: {result['pulse'][-1].max():.4f} (相对值)")
print(f"传播距离: {length} km")

# ── 可视化 ──────────────────────────────────────────
plot_evolution(result, t, w, save_path="01_gaussian_pulse.png")
