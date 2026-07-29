"""Kerr 光频梳模拟 — 基于 Lugiato-Lefever 方程 (LLE)。

LLE: ∂ψ/∂τ = -(1+iα)ψ + i|ψ|²ψ - i(β₂/2)∂²ψ/∂θ² + f
使用对称分步傅里叶法求解。
"""

import numpy as np

def solve_lle(alpha, beta2, pump, n_pts=512, n_steps=3000, dt=0.02, seed=42):
    """求解 LLE，返回腔内场和频谱。

    参数
    ----------
    alpha : float
        失谐参数
    beta2 : float
        色散参数（负=反常，产生孤子梳）
    pump : float
        泵浦振幅
    n_pts : int
        空间离散点数
    n_steps : int
        时间步数
    dt : float
        时间步长
    seed : int
        随机种子

    返回
    -------
    dict : theta, psi, spectrum, snapshots
    """
    theta = np.linspace(0, 2*np.pi, n_pts, endpoint=False)
    k = np.fft.fftfreq(n_pts, theta[1]-theta[0]) * 2*np.pi

    np.random.seed(seed)
    psi = (np.random.randn(n_pts) + 1j*np.random.randn(n_pts)) * 1e-3 + pump

    # 线性算符：损失 + 失谐 + 色散
    lin_op = np.exp((-1 - 1j*alpha + 1j*beta2/2 * k**2) * dt)

    snap_idx = max(1, n_steps // 30)
    snaps = []
    for n in range(n_steps):
        psi = psi * np.exp(1j * np.abs(psi)**2 * dt/2)
        psi = np.fft.ifft(np.fft.fft(psi) * lin_op)
        psi = psi + pump * dt
        psi = psi * np.exp(1j * np.abs(psi)**2 * dt/2)
        if n % snap_idx == 0 or n == n_steps - 1:
            snaps.append(psi.copy())

    return {
        "theta": theta,
        "psi": psi,
        "spectrum": np.abs(np.fft.fftshift(np.fft.fft(psi)))**2,
        "snapshots": np.array(snaps),
    }
