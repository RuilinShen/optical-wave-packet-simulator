"""
光学波包全实验模拟器 - 交互式光学实验台
基于 Streamlit，支持实时调参、即时可视化。

文件结构（按执行顺序）：
  1. 导入+配置   (行 5-28) : 库导入、水印、页面配置
  2. 侧边栏      (行 32-130): 实验选择 + 各层级参数滑块
  3. 赞助验证    (行 135-150): 赞助码输入与验证
  4. 仿真引擎    (行 155-175): SSFM 模拟函数（L1 用）
  5. L1 脉冲显示 (行 180-250): 6个脉冲实验的诊断图 + GIF
  6. L2 可视化   (行 255-380): 5个空间光学/非线性实验
  7. L3 可视化   (行 385-450): 4个光子系统层实验
  8. 导出        (行 455-490): PNG / GIF 导出
  9. 物理说明    (行 495-540): 各实验的物理公式和推导

层级：
  L1 基础层 - 6 个脉冲传播实验（免费试用）
  L2 进阶层 - 5 个空间光学与非线性实验（赞助解锁）
  L3 系统层 - 4 个光子系统实验（赞助解锁）
"""

import sys
sys.path.insert(0, ".")

import streamlit as st
import numpy as np
import matplotlib
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC"]
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
# Also re-set after plt import
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False
# Rebuild font cache to find newly installed fonts
import matplotlib.font_manager
matplotlib.font_manager._load_fontmanager(try_read_cache=False)
# Directly register common Chinese font files
import os as _os
for _fp in ["/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
    if _os.path.exists(_fp):
        matplotlib.font_manager.fontManager.addfont(_fp)
        break
import tempfile, os
from io import BytesIO
import matplotlib.animation as animation
from scipy.fft import fft, fftshift

from src.core import time_grid, freq_grid
from src.sources import gaussian_pulse, sech_pulse, super_gaussian
from src.propagators import ssfm_propagate, ssfm_propagate_dispersion_only
from src.io.sponsor import check_code, get_sponsor_status, get_license_state
from src.sources.beam import gaussian_beam, hermite_gaussian_beam, laguerre_gaussian_beam
from src.propagators.bpm import beam_propagate
from src.media.atmosphere import kolmogorov_phase_screen, apply_phase
from src.nonlinear.polarization import jones_vector, linear_polarization, circular_polarization, birefringent_propagate, stokes_parameters

from src.nonlinear.xpm_fwm import xpm_propagate
st.set_page_config(page_title="光学波包全实验模拟器", page_icon="", layout="wide")

st.markdown("<div style='position:fixed;top:0;left:0;width:100%;height:100%;z-index:2147483647;pointer-events:none;background-image:url(\"data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27300%27 height=%27300%27%3E%3Ctext x=%27150%27 y=%27120%27 font-size=%2720%27 fill=%27%23999%27 fill-opacity=%270.15%27 transform=%27rotate(-30,150,150)%27 text-anchor=%27middle%27 font-family=%27Arial%27%3Eifdian.net/a/S_Physics%3C/text%3E%3Ctext x=%27150%27 y=%27180%27 font-size=%2714%27 fill=%27%23999%27 fill-opacity=%270.15%27 transform=%27rotate(-30,150,150)%27 text-anchor=%27middle%27 font-family=%27Arial%27%3Egithub.com/RuilinShen%3C/text%3E%3C/svg%3E\");background-repeat:repeat;'></div>", unsafe_allow_html=True)
st.title("光学波包全实验模拟器")
st.markdown(r"交互式仿真平台 —— 调节参数，即时观察脉冲在光纤中的传播与演化。")

# ── 侧边栏 ────────────────────────────────────────
# 实验选择器 + 各层级参数滑块
# L1 参数总是显示，L2/L3 参数只在对应实验选中时出现────────────────
st.sidebar.header("实验设置")
st.markdown(r"<style>img{-webkit-user-drag:none;-khtml-user-drag:none;-moz-user-drag:none;-o-user-drag:none;user-drag:none;user-select:none;-webkit-user-select:none;pointer-events:none;-webkit-touch-callout:none;}</style>", unsafe_allow_html=True)
experiment = st.sidebar.selectbox("选择实验场景", [
    "高斯脉冲 GVD 展宽",
    "啁啾脉冲压缩",
    "超高斯脉冲展宽",
    "三阶色散 (TOD)",
    "基态孤子 (N=1)",
    "空间光束衍射",
    "HG/LG 模式",
    "高阶孤子 (N>1)",
    "大气湍流",
    "偏振演化",
    "XPM (交叉相位调制)",
    "定向耦合器",
    "微环谐振腔",
    "锁模激光器",
    "光频梳",
], index=0)
L2_EXPS = ("空间光束衍射", "HG/LG 模式", "大气湍流", "偏振演化", "XPM (交叉相位调制)")
NON_L1_EXPS = L2_EXPS + ("定向耦合器", "微环谐振腔", "锁模激光器", "光频梳")
LICENSED_EXPS = L2_EXPS + ("定向耦合器", "微环谐振腔", "锁模激光器", "光频梳")
license_state = get_license_state()

st.sidebar.markdown("---")
st.sidebar.subheader("物理参数")

T0 = st.sidebar.slider("脉冲宽度 T0 (ps)", 0.2, 5.0, 1.0, 0.1)
beta2 = st.sidebar.slider("GVD beta2 (ps2/km)", -40.0, 40.0, -20.0, 1.0)
length = st.sidebar.slider("传播距离 (km)", 1.0, 30.0, 5.0, 0.5)
beta3 = 0.0
C = 0.0
m = 3
gamma = 0.0
N_order = 1
use_nonlinear = False

if experiment == "啁啾脉冲压缩":
    C = st.sidebar.slider("啁啾参数 C", -5.0, 5.0, 2.0, 0.1)

if experiment == "超高斯脉冲展宽":
    m = st.sidebar.slider("超高斯阶数 m", 1, 5, 3, 1)

if experiment == "三阶色散 (TOD)":
    beta3 = st.sidebar.slider("TOD beta3", -1.0, 1.0, 0.5, 0.05)

if experiment in ("基态孤子 (N=1)", "高阶孤子 (N>1)"):
    gamma = st.sidebar.slider("非线性系数 gamma", 0.5, 5.0, 2.0, 0.1)
    if experiment == "高阶孤子 (N>1)":
        N_order = st.sidebar.slider("孤子阶数 N", 2, 4, 2, 1)
    P0_calc = N_order**2 * abs(beta2) / (gamma * T0**2)
    st.sidebar.markdown(f"  N={N_order} 所需峰值功率: **{P0_calc:.1f} W**")
    use_nonlinear = True

st.sidebar.markdown("---")
if experiment in ("空间光束衍射","HG/LG 模式","大气湍流"):
    wvl = st.sidebar.slider("波长 (nm)", 400, 800, 633, 10) * 1e-9
    w0 = st.sidebar.slider("束腰 (mm)", 0.1, 2.0, 0.5, 0.1) * 1e-3
    if experiment == "大气湍流":
        r0 = st.sidebar.slider("Fried r0 (m)", 0.05, 0.5, 0.2, 0.05)
    else:
        r0 = 0.2
if experiment == "偏振演化":
    pol_theta = st.sidebar.slider("偏振角度 theta (rad)", 0.0, 3.14, 0.0, 0.05)
    pol_phi = st.sidebar.slider("相位延迟 phi (rad)", 0.0, 3.14, 0.0, 0.05)
    delta_n = st.sidebar.slider("双折射 delta_n", 0.0, 0.01, 0.001, 0.0005)
    crystal_L = st.sidebar.slider("晶体长度 (mm)", 0.1, 10.0, 1.0, 0.1)
if experiment == "XPM (交叉相位调制)":
    gamma_val = st.sidebar.slider("非线性系数 gamma", 0.5, 5.0, 2.0, 0.1)
    pump_power = st.sidebar.slider("泵浦功率 (W)", 0.5, 10.0, 2.0, 0.5)
    probe_ratio = st.sidebar.slider("探针相对功率", 0.01, 0.5, 0.05, 0.01)
    xpm_delay = st.sidebar.slider("脉冲延迟 (ps)", -5.0, 5.0, 0.0, 0.5)
if experiment == "HG/LG 模式":
    hg_type = st.sidebar.selectbox("模式类型", ["HG (厄米-高斯)", "LG (拉盖尔-高斯)"])
    hg_m = st.sidebar.slider("HG m (x阶数)", 0, 4, 1, 1)
    hg_n = st.sidebar.slider("HG n (y阶数)", 0, 4, 0, 1)
    lg_p = st.sidebar.slider("LG p (径向阶数)", 0, 3, 0, 1)
    lg_l = st.sidebar.slider("LG l (拓扑荷/OAM)", -5, 5, 1, 1)


if experiment == "定向耦合器":
    dc_wvl = st.sidebar.slider("波长 (nm)", 400, 800, 633, 10) * 1e-9
    dc_w = st.sidebar.slider("波导宽度 (um)", 0.2, 1.0, 0.5, 0.05) * 1e-6
    dc_gap = st.sidebar.slider("波导间距 (um)", 0.1, 2.0, 0.5, 0.05) * 1e-6
    dc_ncore = st.sidebar.slider("芯层折射率", 1.45, 2.0, 1.55, 0.01)
    dc_nclad = st.sidebar.slider("包层折射率", 1.40, 1.50, 1.45, 0.01)
    dc_L = st.sidebar.slider("耦合器长度 (mm)", 0.5, 10.0, 3.0, 0.1) * 1e-3

if experiment == "微环谐振腔":
    mr_wvl_c = st.sidebar.slider("中心波长 (nm)", 1450, 1650, 1550, 5) * 1e-9
    mr_R = st.sidebar.slider("环半径 (um)", 5, 50, 10, 1) * 1e-6
    mr_kappa = st.sidebar.slider("耦合系数 kappa", 0.05, 0.9, 0.2, 0.05)
    mr_alpha = st.sidebar.slider("损耗 alpha (1/m)", 10, 1000, 100, 10)
    mr_neff = st.sidebar.slider("有效折射率 n_eff", 1.5, 3.0, 2.0, 0.05)

if experiment == "锁模激光器":
    ml_g0 = st.sidebar.slider("小信号增益 g0 (/km)", 100, 1000, 600, 50)
    ml_q0 = st.sidebar.slider("可饱和吸收 q0", 0.1, 0.8, 0.3, 0.05)
    ml_R = st.sidebar.slider("输出耦合 R", 0.5, 0.99, 0.9, 0.05)
    ml_nRT = st.sidebar.slider("往返次数", 100, 500, 200, 50)

if experiment == "光频梳":
    comb_alpha = st.sidebar.slider("失谐 alpha", 0.0, 6.0, 3.0, 0.5)
    comb_beta2 = st.sidebar.slider("色散 beta2", -2.0, 0.0, -1.0, 0.1)
    comb_pump = st.sidebar.slider("泵浦振幅 f", 1.0, 5.0, 3.5, 0.1)
n_points = st.sidebar.selectbox("采样点数", [2**10, 2**11, 2**12, 2**13], index=2)

# ── 赞助验证 ──────────────────────────────────────
# 赞助码输入与验证。验证通过后缓存到本地文件。
# 试用模式仅 L1 可用，赞助后解锁 L2+L3────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### 赞助解锁导出")
st.sidebar.caption("项目：光学波包全实验模拟器 | Optical Wave Packet Simulator")
st.sidebar.caption("🔵 赞助码请确认属于光学项目")
if "sponsor_checked" not in st.session_state:
    st.session_state.sponsor_checked = False
    st.session_state.sponsor_valid = False
    st.session_state.sponsor_msg = ""
code_input = st.sidebar.text_input("输入赞助码", placeholder="SPONSOR-XXXX", label_visibility="collapsed")
if st.sidebar.button("验证赞助码", use_container_width=True):
    valid, msg = get_sponsor_status(code_input)
    st.session_state.sponsor_checked = True
    st.session_state.sponsor_valid = valid
    st.session_state.sponsor_msg = msg
if st.session_state.sponsor_valid:
    st.sidebar.success(st.session_state.sponsor_msg)
elif st.session_state.sponsor_checked:
    st.sidebar.error(st.session_state.sponsor_msg)
st.sidebar.markdown("赞助后可获得导出权限")
st.sidebar.markdown("[去爱发电赞助](https://ifdian.net/a/S_Physics)")

# ── 许可证状态
if license_state.get("tier") == "trial":
    st.sidebar.warning(chr(128274) + " 试用模式 — 仅限 L1 基础实验")
else:
    exp = license_state.get("expires_at", "")
    if exp:
        try:
            from datetime import datetime
            rem = (datetime.fromisoformat(exp) - datetime.now()).days + 1
            msg = f"剩余 {rem} 天" if rem > 0 else "已过期"
        except:
            msg = f"有效期至 {exp[:10]}"
    else:
        msg = "永久有效"
    st.sidebar.success(chr(9989) + f" 已赞助（{msg}）")

# ── 仿真函数 ──────────────────────────────────────
@st.cache_data
def run_simulation(experiment, T0, beta2, beta3, length, gamma, C, m, use_nonlinear, n_points, N_order):
    """用分步傅里叶法 (SSFM) 运行 L1 脉冲传播模拟。

    参数：
        experiment : str — 实验名称
        T0 : float   — 脉冲宽度 [ps]
        beta2 : float — 群速度色散 [ps^2/km]
        beta3 : float — 三阶色散 [ps^3/km]
        gamma : float — 非线性系数 [1/(W*km)]
        C : float    — 啁啾参数
        m : int      — 超高斯阶数
        use_nonlinear : bool — 是否启用非线性项
        n_points : int — 采样点数
        N_order : int — 孤子阶数

    返回：
        dict — 含 pulse, spectrum, z, t, w, A0
    """
    Tmax = 5 * T0 + 10
    NT = n_points
    dz = 0.01
    t, dt = time_grid(NT, Tmax)
    w, _ = freq_grid(NT, dt)
    if experiment == "超高斯脉冲展宽":
        A0 = super_gaussian(t, T0, m)
    else:
        A0 = gaussian_pulse(t, T0, C)
    if use_nonlinear:
        P0 = N_order**2 * abs(beta2) / (gamma * T0**2) if gamma > 0 else 1.0
        A0 = A0 * np.sqrt(P0)
        result = ssfm_propagate(A0, t, w, beta2, gamma, length, dz, beta3)
    else:
        result = ssfm_propagate_dispersion_only(A0, t, w, beta2, length, dz, beta3)
    result["t"] = t
    result["w"] = w
    result["A0"] = A0
    return result

data = run_simulation(experiment, T0, beta2, beta3, length, gamma, C, m, use_nonlinear, n_points, N_order)

# ── L2/L3 缓存包装 ─────────────────────
@st.cache_data
def _ml_cached(g0, q0, R, nRT, beta2, ga, np_):
    from src.core import time_grid, freq_grid
    from src.media.laser_cavity import mode_lock_sim
    t_, dt_ = time_grid(np_, 30.0)
    w_, _ = freq_grid(np_, dt_)
    params_ = {"g0": g0, "Esat": 10.0, "q0": q0, "Esat_a": 1.0,
               "R": R, "beta2": beta2, "gamma": ga, "L_cav": 0.001, "loss": 0}
    return mode_lock_sim(t_, w_, params_, nRT)

@st.cache_data
def _comb_cached(alpha, beta2, pump, np_):
    from src.media.kerr_comb import solve_lle
    return solve_lle(alpha=alpha, beta2=beta2, pump=pump, n_pts=np_, n_steps=4000, dt=0.02)

# ── L1 脉冲显示 ──────────────────────────────────
# 6 个脉冲传播实验的诊断图 + 传播动画
# 仅在选中 L1 实验时显示（experiment not in NON_L1_EXPS）─────────────────
if experiment not in NON_L1_EXPS:
    # ── 显示 ──────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        init_peak = np.abs(data["A0"]).max() ** 2
        st.metric("初始峰值功率", f"{init_peak:.2f} W")
    with col2:
        final_peak = data["pulse"][-1].max()
        ratio = final_peak / data["pulse"][0].max() if data["pulse"][0].max() > 0 else 0
        st.metric("峰值变化", f"{ratio:.2f}x")
    with col3:
        z_total = data["z"][-1]
        st.metric("传播距离", f"{z_total:.1f} km")
    with col4:
        nz = len(data["z"])
        st.metric("采样帧数", str(nz))
    t = data["t"]; w = data["w"]; z = data["z"]
    pulse = data["pulse"]; spectrum = data["spectrum"]
    f = fftshift(w) / (2 * np.pi)

    # ── 图 ───────────────────────────────────────────────
    st.subheader("诊断图")
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    st.info("四子图说明 │ 上左=时域波形(蓝输入/红输出) │ 上右=频谱(蓝输入/红输出) │ 下排=脉冲/频谱演化彩图")
    ax1 = axes[0, 0]
    ax1.plot(t, pulse[0] / pulse[0].max(), "b-", lw=1.5, label="z = 0")
    ax1.plot(t, pulse[-1] / pulse[-1].max(), "r--", lw=1.5, label=f"z = {z[-1]:.1f} km")
    ax1.set_xlabel("Time (ps)"); ax1.set_ylabel("强度")
    ax1.set_title("时域波形"); ax1.legend(); ax1.grid(alpha=0.3)
    ax2 = axes[0, 1]
    ax2.plot(f, spectrum[0] / spectrum[0].max(), "b-", lw=1.5, label="z = 0")
    ax2.plot(f, spectrum[-1] / spectrum[-1].max(), "r--", lw=1.5, label=f"z = {z[-1]:.1f} km")
    ax2.set_xlabel("频率 (THz)"); ax2.set_ylabel("Spectrum")
    ax2.set_title("Spectrum"); ax2.legend(); ax2.grid(alpha=0.3)
    ax3 = axes[1, 0]
    extent = [t[0], t[-1], z[0], z[-1]]
    im = ax3.imshow(pulse, aspect="auto", origin="lower", extent=extent, cmap="inferno")
    ax3.set_xlabel("Time (ps)"); ax3.set_ylabel("传播距离 (km)")
    ax3.set_title("脉冲演化")
    plt.colorbar(im, ax=ax3, label="强度")
    ax4 = axes[1, 1]
    extent_f = [f[0], f[-1], z[0], z[-1]]
    im2 = ax4.imshow(spectrum, aspect="auto", origin="lower", extent=extent_f, cmap="inferno")
    ax4.set_xlabel("频率 (THz)"); ax4.set_ylabel("传播距离 (km)")
    ax4.set_title("频谱演化")
    plt.colorbar(im2, ax=ax4, label="强度")
    plt.tight_layout()
    st.pyplot(fig)

    # ---- GIF ----
    st.subheader("脉冲传播动画")
    try:
        n_frames = min(len(z), 50)
        frame_idx = list(range(0, len(z), max(1, len(z)//50)))
        fig_gif, ax_gif = plt.subplots(figsize=(10, 4))
        def upd(frame):
            ax_gif.clear()
            ax_gif.plot(t, pulse[frame]/pulse[frame].max(), "r-", lw=2)
            ax_gif.set_xlabel("Time (ps)"); ax_gif.set_ylabel("强度")
            ax_gif.set_title(f"Pulse at z={z[frame]:.1f} km")
            ax_gif.set_ylim(0, 1.1); ax_gif.grid(alpha=0.3)
        ani = animation.FuncAnimation(fig_gif, upd, frames=frame_idx, interval=80)
        fd, gif_path = tempfile.mkstemp(suffix=".gif")
        os.close(fd)
        ani.save(gif_path, writer="pillow", fps=10)
        plt.close(fig_gif)
        with open(gif_path, "rb") as g:
            gif_bytes = g.read()
        os.unlink(gif_path)
        st.image(gif_bytes, use_container_width=True)
        st.caption(f"Animation z=0 to z={z[-1]:.1f} km")
    except Exception as e:
        st.error(f"GIF error: {e}")
else:
    t = np.linspace(-10, 10, 256)
    z = np.array([0, 1])
    pulse = np.zeros((2, 256))
    fig = None

if experiment in LICENSED_EXPS and not st.session_state.sponsor_valid:
    st.info(chr(128274) + " 该实验需要赞助解锁。前往左侧边栏输入赞助码。")
    st.markdown("[去爱发电赞助](https://ifdian.net/a/S_Physics)")
    st.stop()

# ── L2 可视化 ────────────────────────────────────
# 5 个进阶层实验：空间光束衍射、HG/LG 模式、大气湍流、偏振演化、XPM
# 每个实验有独立的参数滑块和可视化逻辑───────────────
if experiment in L2_EXPS:
    st.subheader("实验结果")
    x = np.linspace(-3e-3, 3e-3, 256)
    X, Y = np.meshgrid(x, x)
    if experiment == "空间光束衍射":
        E0 = gaussian_beam(X, Y, w0)
        res = beam_propagate(E0, X, Y, wvl, 2.0, 30)
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))
        for idx in range(4):
            zi = idx * 7
            I = np.abs(res["fields"][zi])**2
            axes[idx].imshow(I, extent=[x[0]*1e3, x[-1]*1e3, x[0]*1e3, x[-1]*1e3], cmap="inferno")
            axes[idx].set_title(f"z={res["z"][zi]*1e3:.0f}mm")
            axes[idx].axis("off")
        st.pyplot(fig)
        try:
            fig_beam, ax_beam = plt.subplots(figsize=(6, 5))
            n_beam = len(res["z"])
            def upd_beam(fr):
                ax_beam.clear()
                I_beam = np.abs(res["fields"][fr])**2
                ax_beam.imshow(I_beam, extent=[x[0]*1e3, x[-1]*1e3, x[0]*1e3, x[-1]*1e3], cmap="inferno")
                ax_beam.set_title(f"z = {res["z"][fr]*1e3:.1f} mm")
                ax_beam.axis("off")
            ani_beam = animation.FuncAnimation(fig_beam, upd_beam, frames=n_beam, interval=100)
            fd3, beam_gif = tempfile.mkstemp(suffix=".gif")
            os.close(fd3)
            ani_beam.save(beam_gif, writer="pillow", fps=10)
            plt.close(fig_beam)
            with open(beam_gif, "rb") as g:
                st.image(g.read(), use_container_width=True)
            os.unlink(beam_gif)
            st.caption("光束传播动画（角谱法）")
        except Exception as e:
            st.error(f"光束传播: {e}")
        st.markdown("高斯光束在自由空间中传播时因衍射而展宽。上图展示不同传播距离z处的光束截面强度分布。束腰w0越小衍射越显著，发散角theta = lambda/(pi w0)。角谱法核心：A(kx,ky,z)=A(kx,ky,0)*exp(-i(kx^2+ky^2)z/(2k))。")
    elif experiment == "HG/LG 模式":
        if hg_type == "HG (厄米-高斯)":
            E = hermite_gaussian_beam(X, Y, w0, hg_m, hg_n)
            ttl = "HG" + str(hg_m) + str(hg_n)
        else:
            E = laguerre_gaussian_beam(X, Y, w0, lg_p, lg_l)
            ttl = "LG" + str(lg_p) + "_" + str(lg_l)
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        ext_mm = [x[0]*1e3, x[-1]*1e3, x[0]*1e3, x[-1]*1e3]
        im0 = axes[0].imshow(np.abs(E)**2, extent=ext_mm, cmap="inferno")
        axes[0].set_title("强度"); axes[0].axis("off")
        plt.colorbar(im0, ax=axes[0])
        im1 = axes[1].imshow(np.angle(E), extent=ext_mm, cmap="twilight", vmin=-3.14, vmax=3.14)
        axes[1].set_title("相位"); axes[1].axis("off")
        plt.colorbar(im1, ax=axes[1], ticks=[-3.14, 0, 3.14])
        plt.suptitle(ttl, fontsize=14)
        plt.tight_layout()
        st.pyplot(fig)
        st.markdown("当前模式: **" + ttl + "**。左侧为强度分布，右侧为相位分布。通过侧边栏滑块调节模式参数。")
        st.markdown("HG和LG模式是光场的完备正交基。HGmn有m×n个节线，LGpl含涡旋相位。上图展示各模式的强度分布。")
    elif experiment == "大气湍流":
        dx = x[1]-x[0]
        if "turb_seed" not in st.session_state:
            st.session_state.turb_seed = 42
        if st.button("重新生成随机种子", key="turb_reg"):
            st.session_state.turb_seed = np.random.randint(0, 10000)
        phase = kolmogorov_phase_screen(256, dx, r0, seed=st.session_state.turb_seed)
        E0 = gaussian_beam(X, Y, w0)
        E = apply_phase(E0, phase)
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].imshow(phase, cmap="RdBu", extent=[x[0]*1e3, x[-1]*1e3, x[0]*1e3, x[-1]*1e3])
        axes[0].set_title("Kolmogorov Phase Screen")
        axes[1].imshow(np.abs(E)**2, extent=[x[0]*1e3, x[-1]*1e3, x[0]*1e3, x[-1]*1e3], cmap="inferno")
        axes[1].set_title("湍流后光束")
        st.pyplot(fig)
        st.markdown("Kolmogorov相位屏模拟大气湍流对光束的扰动。上图左为相位屏分布，右为经过湍流后的光束强度分布。湍流导致光束扩展和光强闪烁，Fried参数r0越小湍流越强。")
    elif experiment == "偏振演化":
        from src.nonlinear.polarization import jones_vector, stokes_parameters, birefringent_propagate
        J_in = jones_vector(pol_theta, pol_phi)
        wvl_pol = 633e-9
        J_out = birefringent_propagate(J_in, delta_n, crystal_L * 1e-3, wvl_pol)
        S_in = stokes_parameters(J_in)
        S_out = stokes_parameters(J_out)
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        x_pos = [0, 1, 2]
        axes[0].bar(x_pos, [S_in[1]/S_in[0], S_in[2]/S_in[0], S_in[3]/S_in[0]], color='steelblue', alpha=0.8)
        axes[0].set_xticks(x_pos); axes[0].set_xticklabels(["S1","S2","S3"])
        axes[0].set_ylim(-1.1, 1.1); axes[0].axhline(0, color="gray")
        axes[0].set_title("输入 Stokes 参数")
        axes[1].bar(x_pos, [S_out[1]/S_out[0], S_out[2]/S_out[0], S_out[3]/S_out[0]], color='coral', alpha=0.8)
        axes[1].set_xticks(x_pos); axes[1].set_xticklabels(["S1","S2","S3"])
        axes[1].set_ylim(-1.1, 1.1); axes[1].axhline(0, color="gray")
        axes[1].set_title("输出 Stokes（双折射后）")
        plt.tight_layout()
        st.pyplot(fig)
        st.markdown("**实验结果说明**：左侧为输入偏振态的Stokes参数，右侧为经过双折射介质后的输出参数。theta控制偏振角度，phi控制椭圆度。delta_n和晶体长度决定双折射效应。")
    elif experiment == "XPM (交叉相位调制)":
        from src.sources import gaussian_pulse
        from src.core import time_grid, freq_grid
        from scipy.fft import fft, fftshift
        import numpy as np
        Tmax = 5 * T0 + 10
        tx, dtx = time_grid(n_points, Tmax)
        wx, _ = freq_grid(n_points, dtx)
        A1 = gaussian_pulse(tx, T0, 0) * np.sqrt(pump_power)
        pr = probe_ratio
        A2 = gaussian_pulse(tx - xpm_delay, T0, 0) * np.sqrt(2.0 * pr)
        gv = gamma_val
        res_xpm = xpm_propagate(A1, A2, tx, beta2, beta2, gv, length, 0.01)
        fig_xpm, axes_xpm = plt.subplots(2, 2, figsize=(14, 7))
        fx = fftshift(wx) / (2*np.pi)
        sin_s1 = np.abs(fftshift(fft(A1)))**2; sin_s2 = np.abs(fftshift(fft(A2)))**2
        axes_xpm[0,0].plot(fx, sin_s1/sin_s1.max(), label="Pump", lw=1.5)
        axes_xpm[0,0].plot(fx, sin_s2/sin_s2.max(), label="Probe", lw=1.5)
        axes_xpm[0,0].set_title("输入频谱"); axes_xpm[0,0].legend(); axes_xpm[0,0].grid(alpha=0.3)
        axes_xpm[0,0].set_xlabel("f (THz)"); axes_xpm[0,0].set_ylabel("Norm. Intensity")
        sout_s1 = np.abs(fftshift(fft(res_xpm["field1"][-1])))**2
        sout_s2 = np.abs(fftshift(fft(res_xpm["field2"][-1])))**2
        axes_xpm[0,1].plot(fx, sout_s1/sout_s1.max(), label="Pump", lw=1.5)
        axes_xpm[0,1].plot(fx, sout_s2/sout_s2.max(), label="Probe", lw=1.5)
        axes_xpm[0,1].set_title("输出频谱 (XPM broadens probe)"); axes_xpm[0,1].legend()
        axes_xpm[0,1].grid(alpha=0.3); axes_xpm[0,1].set_xlabel("f (THz)")
        ext_xpm = [tx[0], tx[-1], res_xpm["z"][0], res_xpm["z"][-1]]
        im1 = axes_xpm[1,0].imshow(np.abs(res_xpm["field1"])**2, aspect="auto", origin="lower", extent=ext_xpm, cmap="inferno")
        axes_xpm[1,0].set_title("泵浦演化"); axes_xpm[1,0].set_xlabel("Time (ps)"); axes_xpm[1,0].set_ylabel("z (km)")
        plt.colorbar(im1, ax=axes_xpm[1,0])
        im2 = axes_xpm[1,1].imshow(np.abs(res_xpm["field2"])**2, aspect="auto", origin="lower", extent=ext_xpm, cmap="inferno")
        axes_xpm[1,1].set_title("探针演化"); axes_xpm[1,1].set_xlabel("Time (ps)"); axes_xpm[1,1].set_ylabel("z (km)")
        plt.colorbar(im2, ax=axes_xpm[1,1])
        plt.tight_layout()
        fig = fig_xpm
        st.pyplot(fig_xpm)


# ── L3 可视化 ────────────────────────────────────
# 4 个系统层实验：定向耦合器、微环谐振腔、锁模激光器、Kerr 光频梳
# 使用独立的物理模块（waveguide.py, microring.py, laser_cavity.py, kerr_comb.py）───────────────
if experiment == "定向耦合器":
    from src.media.waveguide import coupling_coefficient, coupled_power, dual_waveguide_profile
    st.subheader("定向耦合器模拟")
    kappa_dc = coupling_coefficient(dc_wvl, dc_ncore, dc_nclad, dc_w, dc_gap)
    z_dc, P1_dc, P2_dc = coupled_power(kappa_dc, dc_L, n_points)
    Lc_dc = np.pi / (2 * kappa_dc) if kappa_dc > 0 else 0
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("耦合系数 κ", f"{kappa_dc:.0f} /m")
    col_b.metric("耦合长度 Lc", f"{Lc_dc*1e3:.2f} mm" if Lc_dc > 0 else "N/A")
    cpl_eff = P2_dc[-1]
    col_c.metric("耦合效率", f"{cpl_eff:.1%}")
    fig_dc, axes_dc = plt.subplots(1, 2, figsize=(14, 5))
    axes_dc[0].plot(z_dc*1e3, P1_dc, label="波导 1", lw=2)
    axes_dc[0].plot(z_dc*1e3, P2_dc, label="波导 2", lw=2)
    if Lc_dc > 0:
        axes_dc[0].axvline(Lc_dc*1e3, color="gray", ls="--", alpha=0.5, label=f"Lc={Lc_dc*1e3:.2f}mm")
    axes_dc[0].set_xlabel("z (mm)"); axes_dc[0].set_ylabel("Power")
    axes_dc[0].set_title("功率传输"); axes_dc[0].legend(); axes_dc[0].grid(alpha=0.3)
    x_dc = np.linspace(-3e-6, 3e-6, 1000)
    n_dc = dual_waveguide_profile(x_dc, dc_w, dc_gap, dc_ncore, dc_nclad)
    axes_dc[1].plot(x_dc*1e6, n_dc, "b-", lw=2)
    axes_dc[1].set_xlabel("x (um)"); axes_dc[1].set_ylabel("n")
    axes_dc[1].set_title("折射率截面"); axes_dc[1].grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_dc)
    fig = fig_dc
    st.markdown("两条平行波导之间的功率通过倏逝场来回耦合。功率完全转移所走的距离称为耦合长度 Lc = π/(2κ)。")

if experiment == "微环谐振腔":
    from src.media.microring import ring_transmission, fsr, extinction_ratio, q_factor
    import numpy as np
    st.subheader("微环谐振腔透射谱")
    L_mr = 2 * np.pi * mr_R
    fsr_val = fsr(mr_wvl_c, mr_neff, mr_R)
    span = max(fsr_val * 5, 1e-9)
    wvls_mr = np.linspace(mr_wvl_c - span/2, mr_wvl_c + span/2, 5000)
    T_mr, _ = ring_transmission(wvls_mr, mr_neff, mr_R, mr_kappa, mr_alpha)
    dip_idx = np.argmin(T_mr)
    wvl_res = wvls_mr[dip_idx]
    er = extinction_ratio(mr_kappa, mr_alpha, mr_R)
    Q = q_factor(wvl_res, mr_neff, mr_R, mr_kappa, mr_alpha)
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("共振波长", f"{wvl_res*1e9:.2f} nm")
    col_b.metric("FSR", f"{fsr_val*1e9:.2f} nm")
    col_c.metric("Q 因子", f"{Q:.0f}")
    col_d.metric("消光比", f"{er:.1f} dB")
    fig_mr, ax_mr = plt.subplots(figsize=(14, 5))
    ax_mr.plot(wvls_mr*1e9, T_mr, "b-", lw=1.5)
    ax_mr.axvline(wvl_res*1e9, color="r", ls="--", alpha=0.5, label=f"res @ {wvl_res*1e9:.2f}nm")
    ax_mr.set_xlabel("Wavelength (nm)"); ax_mr.set_ylabel("Transmission")
    ax_mr.set_title("微环透射谱")
    ax_mr.set_ylim(-0.05, 1.05); ax_mr.legend(); ax_mr.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_mr)
    fig = fig_mr

if experiment == "锁模激光器":
    from src.media.laser_cavity import mode_lock_sim
    from src.core import time_grid, freq_grid
    from scipy.fft import fft, fftshift
    st.subheader("锁模激光器腔模拟")
    t_ml, dt_ml = time_grid(n_points, 30.0)
    w_ml, _ = freq_grid(n_points, dt_ml)
    with st.spinner("模拟腔多次往返中..."):
        r_ml = _ml_cached(ml_g0, ml_q0, ml_R, ml_nRT, beta2, gamma, n_points)
    Ef_ml = np.trapezoid(np.abs(r_ml["final_field"])**2, t_ml)
    Pp_ml = np.abs(r_ml["final_field"])**2
    col1, col2, col3 = st.columns(3)
    col1.metric("脉冲能量", f"{Ef_ml:.2f}")
    col2.metric("峰值功率", f"{Pp_ml.max():.2f}")
    fwhm_n = np.sum(Pp_ml > Pp_ml.max()/2)
    col3.metric("脉宽", f"{fwhm_n * dt_ml:.3f} ps")
    fig_ml, axes_ml = plt.subplots(1, 3, figsize=(18, 5))
    ext_ml = [t_ml[0], t_ml[-1], 0, len(r_ml["fields"])-1]
    from matplotlib.colors import LogNorm
    evo_data = np.abs(r_ml["fields"])**2
    vmin_ml = max(evo_data[evo_data > 0].min() if (evo_data > 0).any() else 1e-10, 1e-10)
    im_ml = axes_ml[0].imshow(evo_data, aspect="auto", origin="lower", extent=ext_ml, cmap="inferno", norm=LogNorm(vmin=vmin_ml, vmax=evo_data.max()))
    del evo_data, vmin_ml
    axes_ml[0].set_title("脉冲演化 Over Round-Trips")
    axes_ml[0].set_xlabel("Time (ps)"); axes_ml[0].set_ylabel("Round-Trip")
    plt.colorbar(im_ml, ax=axes_ml[0])
    axes_ml[1].plot(t_ml, np.abs(r_ml["final_field"])**2, "r-", lw=2)
    axes_ml[1].set_title("稳态脉冲"); axes_ml[1].set_xlabel("Time (ps)")
    axes_ml[1].set_ylabel("强度"); axes_ml[1].grid(alpha=0.3)
    f_ml = fftshift(w_ml) / (2*np.pi)
    spec_ml = np.abs(fftshift(fft(r_ml["final_field"])))**2
    axes_ml[2].plot(f_ml, spec_ml / spec_ml.max(), "b-", lw=1.5)
    axes_ml[2].set_title("Spectrum"); axes_ml[2].set_xlabel("频率 (THz)")
    axes_ml[2].grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_ml)
    fig = fig_ml
if experiment == "光频梳":
    from src.media.kerr_comb import solve_lle
    import numpy as np
    st.subheader("Kerr 光频梳模拟")
    with st.spinner("求解 Lugiato-Lefever 方程..."):
        res_comb = _comb_cached(comb_alpha, comb_beta2, comb_pump, 1024)
    spec_comb = res_comb["spectrum"]
    n_peaks = np.sum(spec_comb > spec_comb.max() * 0.01)
    pwr_comb = np.mean(np.abs(res_comb["psi"])**2)
    col1, col2, col3 = st.columns(3)
    col1.metric("梳齿数 (>1%)", str(n_peaks))
    col2.metric("腔内功率", f"{pwr_comb:.2f}")
    col3.metric("泵浦振幅", f"{comb_pump:.1f}")
    fig_comb, axes_comb = plt.subplots(1, 2, figsize=(16, 5))
    freq_comb = np.fft.fftshift(np.fft.fftfreq(len(res_comb["theta"]), res_comb["theta"][1]-res_comb["theta"][0])) * 2*np.pi
    axes_comb[0].plot(freq_comb[freq_comb >= 0], spec_comb[freq_comb >= 0], "b-", lw=1)
    axes_comb[0].set_yscale("log")
    axes_comb[0].set_xlabel("Azimuthal Mode Number k"); axes_comb[0].set_ylabel("Intensity (log)")
    axes_comb[0].set_title("频率梳频谱"); axes_comb[0].grid(alpha=0.3, which="both")
    axes_comb[0].set_xlim(0, min(200, freq_comb[freq_comb >= 0].max()))
    axes_comb[1].plot(res_comb["theta"], np.abs(res_comb["psi"])**2, "r-", lw=1.5)
    axes_comb[1].set_xlabel("theta (rad)"); axes_comb[1].set_ylabel("|psi|^2")
    axes_comb[1].set_title("腔内场分布")
    axes_comb[1].set_xlim(0, 2*np.pi); axes_comb[1].grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig_comb)
    fig = fig_comb
    st.info("Kerr频率梳：强泵浦光在微环中通过四波混频产生等间距频率梳齿。反常色散(beta2<0)和足够高的泵浦是梳子形成的必要条件。")
    st.info("从随机噪声自启动，经过多次往返后通过增益饱和与可饱和吸收体形成稳定锁模脉冲。调节g0/q0可观察脉冲建立过程的变化。")
# ── 导出 ──────────────────────────────────────────
# PNG 和 GIF 导出功能。需要赞助验证通过。
# GIF 仅 L1 实验可用（L2/L3 没有传播动画）───────────────
st.markdown(r"---")
st.subheader("导出" + ("图片 / GIF" if experiment not in NON_L1_EXPS else "图片"))
if st.session_state.sponsor_valid:
    if experiment not in NON_L1_EXPS:
        gif_fps = st.selectbox("GIF 速度", [2, 4, 6, 12], index=2)
    col_a, col_b = st.columns(2)
    with col_a:
        if fig is not None and st.button("导出 PNG 图片", use_container_width=True):
            buf_png = BytesIO()
            fig.savefig(buf_png, format="png", dpi=150, bbox_inches="tight")
            st.download_button("点击下载 PNG", data=buf_png.getvalue(), file_name="diagnostic_plot.png", mime="image/png", use_container_width=True)
    if experiment not in NON_L1_EXPS:
        with col_b:
            if st.button("导出 GIF 动画", use_container_width=True):
                fig_anim, ax_anim = plt.subplots(figsize=(8, 5))
                n_frames = len(z)
                def update(frame):
                    ax_anim.clear()
                    ax_anim.plot(t, pulse[frame]/pulse[frame].max(), "r-", lw=2)
                    ax_anim.set_xlabel("Time (ps)"); ax_anim.set_ylabel("强度")
                    ax_anim.set_title(f"z={z[frame]:.1f} km")
                    ax_anim.set_ylim(0, 1.1); ax_anim.grid(alpha=0.3)
                ani = animation.FuncAnimation(fig_anim, update, frames=n_frames, interval=80)
                fd2, gif_path2 = tempfile.mkstemp(suffix=".gif")
                os.close(fd2)
                ani.save(gif_path2, writer="pillow", fps=gif_fps)
                plt.close(fig_anim)
                with open(gif_path2, "rb") as g:
                    gif_data = g.read()
                os.unlink(gif_path2)
                st.download_button("点击下载 GIF", data=gif_data, file_name="pulse_evolution.gif", mime="image/gif", use_container_width=True)
    st.markdown(r"---")
    st.markdown(r"感谢您的赞助支持！")
else:
    st.info("赞助后可解锁 PNG/GIF 导出功能")
    st.markdown(r"[去爱发电赞助](https://ifdian.net/a/S_Physics)")

# ── 物理说明 ────────────────────────────────────
# 各实验的物理原理、核心公式和相关解释
# 数据驱动渲染：从 PHYSICS_DATA 字典读取内容─────────────
st.subheader("物理说明")
PHYSICS_DATA = {
    "高斯脉冲 GVD 展宽": [
        ("m", r"高斯脉冲在色散光纤中传播，不同频率分量以不同速度传播导致脉冲展宽。"),
        ("l", r"\frac{\partial A}{\partial z} = -i\frac{\beta_2}{2}\frac{\partial^2 A}{\partial T^2}"),
        ("m", r"$L_D=T_0^2/|\beta_2|$ 为色散长度。$T(z)=T_0\sqrt{1+(z/L_D)^2}$。"),
    ],
    "啁啾脉冲压缩": [
        ("m", r"带正啁啾的脉冲在反常色散光纤中先压缩后展宽。"),
        ("l", r"z_{\min} = \frac{|C|}{1+C^2}L_D, \quad T_{\min} = \frac{T_0}{\sqrt{1+C^2}}"),
        ("m", r"压缩条件：$C\beta_2<0$（正啁啾 + 反常色散）。"),
    ],
    "超高斯脉冲展宽": [
        ("m", r"$A(0,T)=\exp(-\frac12|T/T_0|^{2m})$ $m=1$为标准高斯，$m=3$为近矩形脉冲。"),
        ("m", r"超高斯脉冲边缘陡峭→频域分量更丰富，GVD 导致边缘产生振荡结构。"),
    ],
    "三阶色散 (TOD)": [
        ("m", r"三阶色散 ($\beta_3$) 导致脉冲非对称畸变，$\phi(\omega)=\beta_2\omega^2/2+\beta_3\omega^3/6$。"),
        ("m", r"$\beta_3>0$在前沿产生振荡，$\beta_3<0$在后沿，超短脉冲中不可忽略。"),
    ],
    "基态孤子 (N=1)": [
        ("m", r"反常色散 + SPM 精确平衡，形成稳定孤子。"),
        ("l", r"i\frac{\partial A}{\partial z} = -\frac{\beta_2}{2}\frac{\partial^2 A}{\partial T^2} + \gamma |A|^2 A"),
        ("m", r"$N^2=\gamma P_0 T_0^2/|\beta_2|=1$ → $P_0=|\beta_2|/(\gamma T_0^2)$。"),
    ],
    "高阶孤子 (N>1)": [
        ("m", r"N>1 时孤子呈现周期性呼吸行为：压缩→分裂→恢复，周期 $z_0=\pi L_D/2$。"),
        ("m", r"N 越大呼吸越剧烈。参数滑块可调 N=2~4。"),
    ],
    "空间光束衍射": [
        ("m", r"高斯光束在自由空间中传播时因衍射而展宽。光束半径随传播距离变化关系："),
        ("l", r"w(z)=w_0\sqrt{1+(z/z_R)^2},\quad z_R=\pi w_0^2/\lambda"),
        ("m", r"发散角 $\theta = \lambda/(\pi w_0)$，束腰越小衍射越显著。角谱法通过频域相位因子 $\exp(-i(k_x^2+k_y^2)z/(2k))$ 模拟衍射。"),
    ],
    "HG/LG 模式": [
        ("m", r"厄米-高斯(HG)和拉盖尔-高斯(LG)模式是空间光场的完备正交基。"),
        ("l", r"\Psi_{mn}^{\mathrm{HG}}(x,y)=C_{mn}H_m(\sqrt{2}x/w_0)H_n(\sqrt{2}y/w_0)e^{-(x^2+y^2)/w_0^2}"),
        ("l", r"\Psi_{pl}^{\mathrm{LG}}(r,\theta)=C_{pl}(\sqrt{2}r/w_0)^{|l|}L_p^{|l|}(2r^2/w_0^2)e^{-r^2/w_0^2}e^{-il\theta}"),
        ("m", r"HG$_{mn}$有 $m\times n$ 个节线；LG$_{pl}$ 含涡旋相位 $e^{-il\theta}$，$l$ 为拓扑荷数决定OAM。"),
    ],
    "大气湍流": [
        ("m", r"Kolmogorov湍流理论：功率谱 $\Phi_n(\kappa)=0.033 C_n^2 \kappa^{-11/3}$。"),
        ("l", r"\Phi_n(\kappa)=0.033 C_n^2 \kappa^{-11/3},\qquad r_0=[0.423 k^2 C_n^2 L]^{-3/5}"),
        ("m", r"Fried参数 $r_0$ 表征湍流强度。相位屏法模拟大气湍流产生光强闪烁(Scintillation)和波前畸变。"),
    ],
    "偏振演化": [
        ("m", r"偏振态用 Jones 向量 $\mathbf{J}=[E_x e^{i\phi_x}, E_y e^{i\phi_y}]^T$ 表征。"),
        ("l", r"S_0=|E_x|^2+|E_y|^2,\ S_1=|E_x|^2-|E_y|^2,\ S_2=2\mathrm{Re}(E_x^*E_y),\ S_3=2\mathrm{Im}(E_x^*E_y)"),
        ("m", r"H线偏 $\to (1,0,0)$；R圆偏 $\to (0,0,1)$。双折射介质中两偏振分量经历不同相位延迟导致偏振态演化。"),
    ],
    "XPM (交叉相位调制)": [
        ("m", r"交叉相位调制(XPM)：两脉冲共传时一者的非线性相位受另一者强度影响。"),
        ("l", r"\frac{\partial A_1}{\partial z}=-\frac{\beta_2}{2}\frac{\partial^2 A_1}{\partial T^2}+i\gamma(|A_1|^2+2|A_2|^2)A_1"),
        ("l", r"\frac{\partial A_2}{\partial z}=-\frac{\beta_2}{2}\frac{\partial^2 A_2}{\partial T^2}+i\gamma(|A_2|^2+2|A_1|^2)A_2"),
        ("m", r"XPM系数(2)是SPM(1)的两倍。强泵浦光通过XPM调制弱探针光相位，导致探针频谱非对称展宽。"),
    ],
    "定向耦合器": [
        ("m", r"定向耦合器：两根平行波导通过倏逝场耦合。功率在两波导间周期性地来回转移。"),
        ("l", r"P_1(z)=\cos^2(\kappa z),\quad P_2(z)=\sin^2(\kappa z)"),
        ("l", r"L_c = \frac{\pi}{2\kappa},\quad \kappa \approx \frac{2h^2\gamma\,e^{-\gamma g}}{\beta w_\text{eff}(h^2+\gamma^2)}"),
        ("m", r"κ 为耦合系数，g 为波导间距，γ 为倏逝衰减常数。间距越大耦合越弱（指数衰减）。"),
    ],
    "微环谐振腔": [
        ("m", r"微环谐振腔：直波导通过倏逝场耦合到环形波导。当满足谐振条件时，光在环内共振增强，透射谱出现凹陷。"),
        ("l", r"T(\lambda)=\frac{a^2+t^2-2at\cos\phi}{1+a^2t^2-2at\cos\phi},\quad \phi=\frac{2\pi n_\text{eff}L}{\lambda}"),
        ("m", r"$t=\sqrt{1-\kappa^2}$ 为自耦合系数，$a=e^{-\alpha L/2}$ 为往返振幅传输。临界耦合条件 $t=a$ 时消光比最大。"),
        ("l", r"\text{FSR} \approx \frac{\lambda^2}{n_\text{eff}L},\quad Q = \frac{\lambda}{\Delta\lambda_\text{FWHM}}"),
    ],
    "锁模激光器": [
        ("m", r"锁模激光器：腔内增益和可饱和吸收体的联合作用使脉冲自启动并稳定化。"),
        ("l", r"T_R \frac{\partial A}{\partial T} = \left(g - l + \frac{1}{\Omega_g^2}\frac{\partial^2}{\partial t^2} + (\gamma - i\beta_2/2)\frac{\partial^2}{\partial t^2}\right)A + (\gamma_r - i\delta)|A|^2 A"),
    ],
    "光频梳": [
        ("l", r"\frac{\partial\psi}{\partial\tau} = -(1+i\alpha)\psi + i|\psi|^2\psi - i\frac{\beta_2}{2}\frac{\partial^2\psi}{\partial\theta^2} + f"),
        ("m", r"$\alpha$ 为失谐，$\beta_2$ 为色散，$f$ 为泵浦振幅。稳定梳齿在反常色散区形成。"),
    ],
}

# 渲染物理说明
if experiment in PHYSICS_DATA:
    for tp, txt in PHYSICS_DATA[experiment]:
        if tp == "m":
            st.markdown(txt)
        elif tp == "l":
            st.latex(txt)

st.markdown(r"---")
st.caption("光学波包全实验模拟器 | L1 基础层 | 引擎：对称分步傅里叶法 (SSFM)")
