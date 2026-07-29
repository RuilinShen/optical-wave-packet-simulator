"""锁模激光器腔模拟 —— 基于往返集总模型。

初始种子噪声经增益介质、可饱和吸收体、输出耦合镜、色散和SPM的
多次往返后，自启动形成稳定锁模脉冲（孤子锁模）。
"""

import numpy as np
from scipy.fft import fft, ifft

def mode_lock_sim(t, w, params, n_rounds=500):
    """运行锁模激光器腔模拟。

    参数
    ----------
    t : ndarray
        时间网格 [ps]
    w : ndarray
        角频率网格 [rad/ps]
    params : dict
        物理参数字典：
            g0      : 小信号增益系数 (1/cm)
            Esat    : 增益饱和能量 [nJ]
            q0      : 可饱和吸收体调制深度
            Esat_a  : 吸收体饱和能量 [nJ]
            R       : 输出耦合镜反射率
            beta2   : GVD [ps²/km]
            gamma   : 非线性系数 [1/(W·km)]
            L_cav   : 腔长 [km] 等效
            loss    : 腔损耗 (1/cm) 额外
    n_rounds : int
        往返次数

    返回
    -------
    result : dict
        z           : 往返索引
        fields      : 每个往返的输出脉冲场
        pulse_energies : 脉冲能量演化
        final_field : 稳态脉冲场
        spectrum    : 稳态光谱
    """
    dt = t[1] - t[0]
    A = 1e-3 * (np.random.randn(len(t)) + 1j * np.random.randn(len(t)))  # 初始噪声
    A = A * np.exp(-t**2 / (2 * (t.max()/6)**2))  # 弱时间限制

    p = params
    dz = p.get("L_cav", 0.001)  # km
    op = np.exp(1j * p["beta2"] / 2 * w**2 * dz / 2)  # 色散算符（半步步长）

    fields, energies = [], []
    for n in range(n_rounds):
        E_p = np.trapezoid(np.abs(A)**2, t)  # 脉冲能量

        # 1. 增益（饱和）
        g = p["g0"] / (1 + E_p / p["Esat"])
        A = A * np.exp(g * dz / 2)  # 场幅增益（功率增益=exp(g*dz)）（增益介质长度 ≈ dz）

        # 2. 可饱和吸收体
        q = p["q0"] / (1 + E_p / p["Esat_a"])
        A = A * np.exp(-q / 2)

        # 3. 额外腔损耗
        A = A * np.exp(-p.get("loss", 0.0) * dz)

        # 4. 输出耦合
        A = A * np.sqrt(p["R"])
        output = A * np.sqrt(1 - p["R"])

        # 5. 色散 + SPM（对称分步傅里叶）
        A = ifft(fft(A) * op)
        A = A * np.exp(1j * p["gamma"] * np.abs(A)**2 * dz)
        A = ifft(fft(A) * op)

        if n % max(1, n_rounds // 100) == 0 or n == n_rounds - 1:
            fields.append(output.copy())
            energies.append(E_p)

    return {
        "z": np.arange(len(fields)),
        "fields": np.array(fields),
        "energies": np.array(energies),
        "final_field": fields[-1],
    }
