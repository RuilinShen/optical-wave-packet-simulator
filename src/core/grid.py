import numpy as np
from scipy.fft import fftfreq


def time_grid(NT, Tmax):
    """
    生成时间网格。

    参数
    ----------
    NT : int
        时间采样点数（通常为 2 的幂，如 2**12）
    Tmax : float
        时间窗口半宽 [ps]

    返回
    -------
    t : ndarray, shape (NT,)
        时间数组，范围 [-Tmax, Tmax - dt)
    dt : float
        时间步长 [ps]
    """
    dt = 2 * Tmax / NT
    t = np.linspace(-Tmax, Tmax - dt, NT)
    return t, dt


def freq_grid(NT, dt):
    """
    生成角频率网格。

    参数
    ----------
    NT : int
        采样点数
    dt : float
        时间步长 [ps]

    返回
    -------
    w : ndarray, shape (NT,)
        角频率数组 [rad/ps]，顺序对应 np.fft.fft 的输出
    dw : float
        角频率步长 [rad/ps]
    """
    dw = 2 * np.pi / (NT * dt)
    w = fftfreq(NT, dt) * 2 * np.pi
    return w, dw
