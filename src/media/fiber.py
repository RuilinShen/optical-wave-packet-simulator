"""
光纤介质模型。
提供色散频域响应函数。
"""

import numpy as np


def dispersion_operator(w, beta2, dz, beta3=0.0):
    """
    生成色散算符（频域）。

    对于非线性薛定谔方程中的色散项，
    频域解为 exp(i * (beta2/2 * w^2 + beta3/6 * w^3) * dz)。
    对称 SSFM 中前半步/后半步用 dz/2。

    参数
    ----------
    w : ndarray
        角频率数组 [rad/ps]
    beta2 : float
        群速度色散 GVD [ps^2/km]
    dz : float
        传播步长 [km]
    beta3 : float, optional
        三阶色散 TOD [ps^3/km]

    返回
    -------
    op : ndarray
        频域色散相位因子 exp(i * (beta2/2 * w^2 + beta3/6 * w^3) * dz)
    """
    phase = 0.5 * beta2 * w**2 + (1/6) * beta3 * w**3
    return np.exp(1j * phase * dz)
