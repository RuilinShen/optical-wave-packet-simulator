"""
诊断绘图工具。
将传播结果可视化为时域、频谱、演化图。
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftshift


def plot_evolution(result, t, w, A0=None, save_path=None):
    """
    绘制四子图诊断：时域 / 频谱 / 脉冲演化 / 频谱演化。

    参数
    ----------
    result : dict
        ssfm_propagate 的返回结果
    t : ndarray
        时间坐标 [ps]
    w : ndarray
        角频率坐标 [rad/ps]
    A0 : ndarray, optional
        初始场（若不提供则用第一帧）
    save_path : str, optional
        图片保存路径，不提供则 plt.show()
    """
    z = result["z"]
    pulse = result["pulse"]
    spectrum = result["spectrum"]

    if A0 is None:
        A0 = pulse[0]  # 从第一帧恢复

    # 频率坐标（THz）
    f = fftshift(w) / (2 * np.pi)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 左上：时域对比
    ax1 = axes[0, 0]
    ax1.plot(t, pulse[0] / pulse[0].max(), "b-", lw=1.5, label="z = 0")
    ax1.plot(t, pulse[-1] / pulse[-1].max(), "r--", lw=1.5,
             label=f"z = {z[-1]:.1f} km")
    ax1.set_xlabel("Time (ps)")
    ax1.set_ylabel("Normalized Intensity")
    ax1.set_title("Temporal Profile")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # 右上：频谱对比
    ax2 = axes[0, 1]
    ax2.plot(f, spectrum[0] / spectrum[0].max(), "b-", lw=1.5, label="z = 0")
    ax2.plot(f, spectrum[-1] / spectrum[-1].max(), "r--", lw=1.5,
             label=f"z = {z[-1]:.1f} km")
    ax2.set_xlabel("Frequency (THz)")
    ax2.set_ylabel("Normalized Spectrum")
    ax2.set_title("Spectrum")
    ax2.legend()
    ax2.grid(alpha=0.3)

    # 左下：脉冲演化
    ax3 = axes[1, 0]
    extent = [t[0], t[-1], z[0], z[-1]]
    im = ax3.imshow(pulse, aspect="auto", origin="lower",
                    extent=extent, cmap="inferno")
    ax3.set_xlabel("Time (ps)")
    ax3.set_ylabel("Distance (km)")
    ax3.set_title("Pulse Evolution")
    plt.colorbar(im, ax=ax3, label="Intensity")

    # 右下：频谱演化
    ax4 = axes[1, 1]
    extent_f = [f[0], f[-1], z[0], z[-1]]
    im2 = ax4.imshow(spectrum, aspect="auto", origin="lower",
                     extent=extent_f, cmap="inferno")
    ax4.set_xlabel("Frequency (THz)")
    ax4.set_ylabel("Distance (km)")
    ax4.set_title("Spectrum Evolution")
    plt.colorbar(im2, ax=ax4, label="Intensity")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")

    plt.show()
