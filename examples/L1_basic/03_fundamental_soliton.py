"""
实验 1.3：基态孤子形成
物理：反常色散 + 自相位调制 → 孤子（色散与非线性平衡）
方法：对称 SSFM，含非线性项
"""

import sys
sys.path.insert(0, ".")

import numpy as np
from src.core import time_grid, freq_grid
from src.sources import gaussian_pulse
from src.propagators import ssfm_propagate
from src.observables import plot_evolution

# ── 参数 ────────────────────────────────────────────
T0 = 1.0          # 脉冲宽度 [ps]
beta2 = -20.0     # GVD [ps^2/km]（反常色散）
gamma = 2.0       # 非线性系数 [1/(km.W)]
length = 20.0     # 传播距离 [km]
dz = 0.01         # 步长 [km]
NT = 2**12        # 采样点数
Tmax = 20.0       # 时间窗口 [ps]

# ── 网格 ────────────────────────────────────────────
t, dt = time_grid(NT, Tmax)
w, _ = freq_grid(NT, dt)

# ── 初始脉冲 ────────────────────────────────────────
A0 = gaussian_pulse(t, T0, C=0.0)

# ── 孤子条件（N=1） ─────────────────────────────────
P0 = abs(beta2) / (gamma * T0**2)
A0 = A0 * np.sqrt(P0)

print(f"基态孤子 (N=1):")
print(f"  峰值功率 P0 = {P0:.2f} W")
print(f"  传播距离 = {length} km")

# ── 传播 ────────────────────────────────────────────
result = ssfm_propagate(A0, t, w, beta2, gamma, length, dz)

# ── 可视化 ──────────────────────────────────────────
plot_evolution(result, t, w, save_path="03_fundamental_soliton.png")
