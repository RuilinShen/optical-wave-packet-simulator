"""波导结构与定向耦合器物理模块。

提供对称平板波导的 TE₀ 模式求解和定向耦合器耦合系数计算。
"""

import numpy as np

def find_neff(wvl, n_core, n_clad, w):
    """求解对称平板波导 TE₀ 模的有效折射率 n_eff。

    参数
    ----------
    wvl : float
        真空中波长 [m]
    n_core, n_clad : float
        芯层/包层折射率
    w : float
        波导宽度 [m]

    返回
    -------
    n_eff : float
        有效折射率，低于截止时返回 n_clad
    """
    k0 = 2 * np.pi / wvl
    V = k0 * w * np.sqrt(n_core**2 - n_clad**2)

    if V < 1e-6:
        return n_clad

    # 对称平板 TE₀ 模的色散方程：
    # V·√(1-b) = 2·arctan(√(b/(1-b)))
    # b = (n_eff² - n_clad²) / (n_core² - n_clad²)
    def f(b):
        if b <= 0 or b >= 1:
            return 1e6 * (0.5 - b)
        return V * np.sqrt(1 - b) - 2 * np.arctan(np.sqrt(b / (1 - b)))

    # 二分法求解归一化传播常数 b
    b_low, b_high = 1e-10, 1 - 1e-10
    f_low, f_high = f(b_low), f(b_high)

    if f_low * f_high > 0:
        return n_clad if V < 0.5 else n_core  # 低于截止或强约束

    for _ in range(100):
        b_mid = (b_low + b_high) / 2
        f_mid = f(b_mid)
        if f_low * f_mid < 0:
            b_high = b_mid
        else:
            b_low, f_low = b_mid, f_mid
        if abs(b_high - b_low) < 1e-12:
            break

    b = (b_low + b_high) / 2
    return np.sqrt(n_clad**2 + b * (n_core**2 - n_clad**2))


def coupling_coefficient(wvl, n_core, n_clad, w=0.5e-6, gap=0.5e-6):
    """计算对称定向耦合器的耦合系数 κ [1/m]。

    基于 Marcuse 耦合模理论，适用于弱导弱耦合情况。
    κ ≈ (2·h²·γ·exp(-γ·gap)) / (β·w_eff·(h²+γ²))
    其中 h=√(k₀²(n_core²-n_eff²))，γ=√(k₀²(n_eff²-n_clad²))
    """
    k0 = 2 * np.pi / wvl
    n_eff = find_neff(wvl, n_core, n_clad, w)

    if n_eff <= n_clad:
        return 0.0

    beta = k0 * n_eff
    h2 = k0**2 * (n_core**2 - n_eff**2)
    g2 = k0**2 * (n_eff**2 - n_clad**2)

    if h2 <= 0 or g2 <= 0:
        return 0.0

    h = np.sqrt(h2)
    gamma = np.sqrt(g2)
    w_eff = w + 2 / gamma
    kappa = (2 * h**2 * gamma * np.exp(-gamma * gap)) / (beta * w_eff * (h**2 + gamma**2))
    return abs(kappa)


def coupled_power(kappa, L, n_points=500):
    """计算两波导中的功率随传播距离 z 的变化。

    P1(z) = cos²(κz), P2(z) = sin²(κz)
    返回 (z, P1, P2)
    """
    z = np.linspace(0, L, n_points)
    phase = kappa * z
    return z, np.cos(phase)**2, np.sin(phase)**2


def dual_waveguide_profile(x, w=0.5e-6, gap=0.5e-6, n_core=1.55, n_clad=1.45):
    """生成双波导截面的折射率分布。"""
    n = np.full_like(x, n_clad)
    half_w = w / 2
    half_gap = gap / 2
    left_c = -half_w - half_gap
    right_c = half_w + half_gap
    n[(x >= left_c - half_w) & (x <= left_c + half_w)] = n_core
    n[(x >= right_c - half_w) & (x <= right_c + half_w)] = n_core
    return n
