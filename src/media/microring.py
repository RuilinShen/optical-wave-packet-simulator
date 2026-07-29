"""微环谐振腔物理模块。

单直波导-环耦合（through-port）透射谱计算。
支持共振波长、FSR、Q 因子等关键指标。
"""

import numpy as np

def ring_transmission(wvls, n_eff, R, kappa, alpha=0.0):
    """计算 through-port 透射谱。

    参数
    ----------
    wvls : ndarray
        波长扫描范围 [m]
    n_eff : float
        有效折射率
    R : float
        环半径 [m]
    kappa : float
        直波导-环耦合系数 (0~1)
    alpha : float
        环内损耗系数 [1/m]

    返回
    -------
    T : ndarray
        透射率 (0~1)，与 wvls 同形状
    phi : ndarray
        对应的往返相位
    """
    L = 2 * np.pi * R
    t = np.sqrt(max(0, 1 - kappa**2))
    a = np.exp(-alpha * L / 2) if alpha > 0 else 1.0
    a = max(a, 1e-12)

    phi = 2 * np.pi * n_eff * L / wvls
    cos_phi = np.cos(phi)
    num = a**2 + t**2 - 2 * a * t * cos_phi
    den = 1 + a**2 * t**2 - 2 * a * t * cos_phi
    return np.where(den > 1e-15, num / den, 0.0), phi


def fsr(wvl, n_eff, R):
    """自由光谱范围 FSR [m]  (波长域近似)。"""
    L = 2 * np.pi * R
    return wvl**2 / (n_eff * L)


def extinction_ratio(kappa, alpha, R):
    """共振峰消光比 [dB]。"""
    L = 2 * np.pi * R
    t = np.sqrt(max(0, 1 - kappa**2))
    a = np.exp(-alpha * L / 2) if alpha > 0 else 1.0
    if a * t >= 1:
        return 0.0
    T_min = ((a - t) / (1 - a * t))**2
    T_max = ((a + t) / (1 + a * t))**2
    if T_min <= 0 or T_max <= 0:
        return 40.0
    return min(40.0, 10 * np.log10(T_max / T_min))


def q_factor(wvl_res, n_eff, R, kappa, alpha=0.0):
    """近似品质因子 Q ≈ λ_res / Δλ_FWHM。"""
    L = 2 * np.pi * R
    t = np.sqrt(max(0, 1 - kappa**2))
    a = np.exp(-alpha * L / 2) if alpha > 0 else 1.0
    a = max(a, 1e-12)
    fwhm_est = wvl_res**2 / (np.pi * L * n_eff) * (1 - a * t) / np.sqrt(max(a * t, 1e-15))
    return wvl_res / max(fwhm_est, 1e-15)
