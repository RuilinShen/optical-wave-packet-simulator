import math
"""
空间光束生成器。
提供厄米-高斯 (HG) 和拉盖尔-高斯 (LG) 模式。
"""

import numpy as np
from scipy.special import eval_hermite, eval_genlaguerre


def hermite_gaussian_beam(X, Y, w0, m=0, n=0):
    """
    生成厄米-高斯光束 HG_mn。

    参数
    ----------
    X, Y : ndarray
        空间坐标网格 [m]
    w0 : float
        束腰半径 [m]
    m, n : int
        x 和 y 方向的模式阶数

    返回
    -------
    E : ndarray
        复数场分布
    """
    u = np.sqrt(2) * X / w0
    v = np.sqrt(2) * Y / w0
    Hm = eval_hermite(m, u)
    Hn = eval_hermite(n, v)
    r2 = X**2 + Y**2
    # 归一化常数
    C = np.sqrt(2 / (np.pi * w0**2 * 2**(m+n) * math.factorial(m) * math.factorial(n)))
    E = C * Hm * Hn * np.exp(-r2 / w0**2)
    return E


def laguerre_gaussian_beam(X, Y, w0, p=0, l=1):
    """
    生成拉盖尔-高斯光束 LG_pl（含涡旋相位）。

    参数
    ----------
    X, Y : ndarray
        空间坐标网格 [m]
    w0 : float
        束腰半径 [m]
    p : int
        径向阶数
    l : int
        角向阶数（拓扑荷数，决定 OAM）

    返回
    -------
    E : ndarray
        复数场分布（含 exp(-il*theta) 涡旋相位）
    """
    r = np.sqrt(X**2 + Y**2)
    theta = np.arctan2(Y, X)
    r2 = r**2
    # 广义拉盖尔多项式
    L = eval_genlaguerre(p, abs(l), 2 * r2 / w0**2)
    # 归一化常数
    C = np.sqrt(2 * math.factorial(p) / (np.pi * w0**2 * math.factorial(p + abs(l))))
    amp = C * (np.sqrt(2) * r / w0)**abs(l) * L * np.exp(-r2 / w0**2)
    phase = np.exp(-1j * l * theta)
    return amp * phase


def gaussian_beam(X, Y, w0):
    """
    生成基模高斯光束（HG_00 的简写）。
    """
    return hermite_gaussian_beam(X, Y, w0, 0, 0)
