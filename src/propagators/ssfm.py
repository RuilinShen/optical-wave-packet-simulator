"""
对称分步傅里叶法 (SSFM) 传播器。
非线性薛定谔方程的主力数值解法。
"""

import numpy as np
from scipy.fft import fft, ifft, fftshift

from src.core import time_grid, freq_grid
from src.media import dispersion_operator
from src.nonlinear import kerr_operator


def ssfm_propagate(A0, t, w, beta2, gamma, length, dz, beta3=0.0,
                   store_every=None):
    """
    对称 SSFM 传播。

    参数
    ----------
    A0 : ndarray
        初始场包络
    t : ndarray
        时间坐标 [ps]
    w : ndarray
        角频率坐标 [rad/ps]
    beta2 : float
        GVD 系数 [ps^2/km]
    gamma : float
        非线性系数 [1/(km.W)]
    length : float
        总传播距离 [km]
    dz : float
        步长 [km]
    beta3 : float, optional
        TOD 系数 [ps^3/km]
    store_every : int, optional
        每多少步存一帧，默认自动设为约 20 帧

    返回
    -------
    result : dict
        A_out      - 最终场
        z          - 存储位置数组
        pulse      - 脉冲强度演化 [len(z), NT]
        spectrum   - 频谱演化 [len(z), NT]
    """
    Nz = int(length / dz)
    if store_every is None:
        store_every = max(1, Nz // 20)

    # 色散算符（前半步/后半步共用）
    disp_op = dispersion_operator(w, beta2, dz / 2, beta3)

    z_list = []
    pulse_list = []
    spec_list = []

    A = A0.copy()

    for n in range(Nz):
        # ① 前半色散（频域）
        A = ifft(fft(A) * disp_op)

        # ② 非线性（实空间）
        A = kerr_operator(A, gamma, dz)

        # ③ 后半色散（频域）
        A = ifft(fft(A) * disp_op)

        # 存储
        if n % store_every == 0 or n == Nz - 1:
            z_list.append(n * dz)
            pulse_list.append(np.abs(A) ** 2)
            spec_list.append(np.abs(fftshift(fft(A))) ** 2)

    return {
        "A_out": A,
        "z": np.array(z_list),
        "pulse": np.array(pulse_list),
        "spectrum": np.array(spec_list),
    }


def ssfm_propagate_dispersion_only(A0, t, w, beta2, length, dz, beta3=0.0,
                                   store_every=None):
    """
    纯色散传播（无非线性）。
    简化版，用于 L1 基础实验。
    """
    Nz = int(length / dz)
    if store_every is None:
        store_every = max(1, Nz // 20)

    disp_op = dispersion_operator(w, beta2, dz / 2, beta3)

    z_list = []
    pulse_list = []
    spec_list = []

    A = A0.copy()

    for n in range(Nz):
        A = ifft(fft(A) * disp_op)
        A = ifft(fft(A) * disp_op)

        if n % store_every == 0 or n == Nz - 1:
            z_list.append(n * dz)
            pulse_list.append(np.abs(A) ** 2)
            spec_list.append(np.abs(fftshift(fft(A))) ** 2)

    return {
        "A_out": A,
        "z": np.array(z_list),
        "pulse": np.array(pulse_list),
        "spectrum": np.array(spec_list),
    }
