"""
克尔非线性模块。
提供自相位调制 (SPM) 的非线性相位因子。
"""

import numpy as np


def nonlinear_phase(gamma, intensity, dz):
    """
    计算 SPM 非线性相位因子。

    SSFM 中非线性步在实空间执行：
    A_out = A_in * exp(i * gamma * |A_in|^2 * dz)

    参数
    ----------
    gamma : float
        非线性系数 [1/(km·W)]
    intensity : ndarray
        瞬时功率 |A|^2 [W]
    dz : float
        传播步长 [km]

    返回
    -------
    phase_factor : ndarray
        非线性相位因子 exp(i * gamma * |A|^2 * dz)
    """
    return np.exp(1j * gamma * intensity * dz)


def kerr_operator(A, gamma, dz):
    """
    对场施加克尔非线性。

    参数
    ----------
    A : ndarray
        当前场包络
    gamma : float
        非线性系数 [1/(km·W)]
    dz : float
        传播步长 [km]

    返回
    -------
    A_out : ndarray
        施加非线性后的场
    """
    return A * nonlinear_phase(gamma, np.abs(A) ** 2, dz)
