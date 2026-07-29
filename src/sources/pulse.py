"""
脉冲生成器。
提供 SSFM 模拟所需的各种初始脉冲形状。
"""

import numpy as np


def gaussian_pulse(t, T0, C=0.0):
    """
    生成高斯脉冲包络。

    参数
    ----------
    t : ndarray
        时间数组 [ps]
    T0 : float
        脉冲宽度 [ps] (1/e 半宽)
    C : float, optional
        啁啾参数。C=0 无啁啾，C>0 正啁啾，C<0 负啁啾。

    返回
    -------
    A : ndarray
        复数包络 A(t)
    """
    return np.exp(-0.5 * (1 + 1j * C) * (t / T0) ** 2)


def sech_pulse(t, T0):
    """
    生成双曲正割脉冲包络（孤子标准形状）。

    参数
    ----------
    t : ndarray
        时间数组 [ps]
    T0 : float
        脉冲宽度 [ps] (1/e 半宽)

    返回
    -------
    A : ndarray
        复数包络 A(t)
    """
    return 1.0 / np.cosh(t / T0)


def super_gaussian(t, T0, m=3):
    """
    生成超高斯脉冲包络。

    参数
    ----------
    t : ndarray
        时间数组 [ps]
    T0 : float
        脉冲宽度 [ps]
    m : int, optional
        超高斯阶数。m=1 为标准高斯，m=3 为近矩形脉冲。

    返回
    -------
    A : ndarray
        实数包络 A(t)
    """
    return np.exp(-0.5 * (np.abs(t) / T0) ** (2 * m))
