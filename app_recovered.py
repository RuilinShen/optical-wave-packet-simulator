data:image/svg+xml,
光学波包全实验模拟器 - 交互式光学实验台
基于 Streamlit，支持实时调参、即时可视化。
"""

import sys
sys.path.insert(0, ".")

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import tempfile, os
from scipy.fft import fft, fftshift

from src.core import time_grid, freq_grid
from src.sources import gaussian_pulse, sech_pulse, super_gaussian
from src.propagators import ssfm_propagate, ssfm_propagate_dispersion_only
from src.io import check_code, get_sponsor_status
import matplotlib.animation as animation
from io import BytesIO


st.set_page_config(
    page_title="光学波包全实验模拟器",
    page_icon="",
    layout="wide",
)

st.markdown("""<style>img{-webkit-user-drag:none;-khtml-user-drag:none;-moz-user-drag:none;-o-user-drag:none;user-drag:none;user-select:none;-webkit-user-select:none;pointer-events:none;-webkit-touch-callout:none;}</style>""", unsafe_allow_html=True)
st.markdown("<style>.stApp::after{content:\"\";position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:2147483647;background-image:url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><text x='150' y='120' font-size='20' fill='#999' fill-opacity='0.15' transform='rotate(-30,150,150)' text-anchor='middle' font-family='Arial'>ifdian.net/a/S_Physics</text><text x='150' y='180' font-size='14' fill='#999' fill-opacity='0.15' transform='rotate(-30,150,150)' text-anchor='middle' font-family='Arial'></text></svg>\");background-repeat:repeat;background-size:300px 300px;}</style>", unsafe_allow_html=True)
st.title("光学波包全实验模拟器")
st.markdown("交互式仿真平台 —— 调节参数，即时观察脉冲在光纤中的传播与演化。")


# ── 侧边栏：参数控制 ──────────────────────────────
st.sidebar.header("实验设置")

experiment = st.sidebar.selectbox(
    "选择实验场景",
    [
        "高斯脉冲 GVD 展宽",
        "啁啾脉冲压缩",
        "超高斯脉冲展宽",
        "基态孤子 (N=1)",
    ],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.subheader("物理参数")

T0 = st.sidebar.slider("脉冲宽度 T0 (ps)", 0.2, 5.0, 1.0, 0.1)
beta2 = st.sidebar.slider("GVD β₂ (ps²/km)", -40.0, 40.0, -20.0, 1.0)

gamma = 0.0
length = st.sidebar.slider("传播距离 (km)", 1.0, 30.0, 5.0, 0.5)

if experiment == "啁啾脉冲压缩":
    C = st.sidebar.slider("啁啾参数 C", -5.0, 5.0, 2.0, 0.1)
    m = st.sidebar.slider("超高斯阶数 m", 1, 5, 3, 1)
else:
    C = 0.0
    m = 3

if experiment == "基态孤子 (N=1)":
    gamma = st.sidebar.slider("非线性系数 γ (1/km·W)", 0.5, 5.0, 2.0, 0.1)
    P0_calc = abs(beta2) / (gamma * T0**2)
    st.sidebar.markdown(f"  N=1 所需峰值功率: **{P0_calc:.1f} W**")
    use_nonlinear = True
else:
    gamma = 0.0
    use_nonlinear = False

st.sidebar.markdown("---")
n_points = st.sidebar.selectbox("采样点数", [2**10, 2**11, 2**12, 2**13], index=2)
st.sidebar.markdown("---")
st.sidebar.markdown("### 赞助解锁导出")
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
st.sidebar.markdown("赞助后可获得导出权限，将实验动画导出为 GIF/MP4。")
st.sidebar.markdown("[去爱发电赞助](https://ifdian.net/a/S_Physics)")


# ── 核心计算 ──────────────────────────────────────
@st.cache_data
def run_simulation(experiment, T0, beta2, length, gamma, C,
                   use_nonlinear, n_points):
    """运行 SSFM 模拟并返回结果。"""
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
        P0 = abs(beta2) / (gamma * T0**2) if gamma > 0 else 1.0
        A0 = A0 * np.sqrt(P0)
        result = ssfm_propagate(A0, t, w, beta2, gamma, length, dz)
    else:
        result = ssfm_propagate_dispersion_only(
            A0, t, w, beta2, length, dz
        )

    result["t"] = t
    result["w"] = w
    result["A0"] = A0
    return result


data = run_simulation(experiment, T0, beta2, length, gamma, C,
                      use_nonlinear, n_points)



# ── 结果显示 ──────────────────────────────────────
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

t = data["t"]
w = data["w"]
z = data["z"]
pulse = data["pulse"]
spectrum = data["spectrum"]
f = fftshift(w) / (2 * np.pi)

# ── 绘图 ──────────────────────────────────────────
st.subheader("诊断图")
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
ax1 = axes[0, 0]
ax1.plot(t, pulse[0] / pulse[0].max(), "b-", lw=1.5, label="z = 0")
ax1.plot(t, pulse[-1] / pulse[-1].max(), "r--", lw=1.5, label=f"z = {z[-1]:.1f} km")
ax1.set_xlabel("Time (ps)")
ax1.set_ylabel("Normalized Intensity")
ax1.set_title("Temporal Profile")
ax1.legend()
ax1.grid(alpha=0.3)
ax2 = axes[0, 1]
ax2.plot(f, spectrum[0] / spectrum[0].max(), "b-", lw=1.5, label="z = 0")
ax2.plot(f, spectrum[-1] / spectrum[-1].max(), "r--", lw=1.5, label=f"z = {z[-1]:.1f} km")
ax2.set_xlabel("Frequency (THz)")
ax2.set_ylabel("Normalized Spectrum")
ax2.set_title("Spectrum")
ax2.legend()
ax2.grid(alpha=0.3)
ax3 = axes[1, 0]
extent = [t[0], t[-1], z[0], z[-1]]
im = ax3.imshow(pulse, aspect="auto", origin="lower", extent=extent, cmap="inferno")
ax3.axhline(y=z[-1], color="cyan", lw=1.5, linestyle="--")
ax3.set_xlabel("Time (ps)")
ax3.set_ylabel("Distance (km)")
ax3.set_title("Pulse Evolution")
plt.colorbar(im, ax=ax3, label="Intensity")
ax4 = axes[1, 1]
extent_f = [f[0], f[-1], z[0], z[-1]]
im2 = ax4.imshow(spectrum, aspect="auto", origin="lower", extent=extent_f, cmap="inferno")
ax4.axhline(y=z[-1], color="cyan", lw=1.5, linestyle="--")
ax4.set_xlabel("Frequency (THz)")
ax4.set_ylabel("Distance (km)")
ax4.set_title("Spectrum Evolution")
plt.colorbar(im2, ax=ax4, label="Intensity")
plt.tight_layout()
st.pyplot(fig)

# ── 脉冲动画 ──────────────────────────────────────────
st.subheader("脉冲传播动画")
try:
    n_frames = min(len(z), 50)
    frame_idx = list(range(0, len(z), max(1, len(z)//50)))
    fig_gif, ax_gif = plt.subplots(figsize=(10, 4))
    def upd(frame):
        ax_gif.clear()
        ax_gif.plot(t, pulse[frame] / pulse[frame].max(), "r-", lw=2)
        ax_gif.set_xlabel("Time (ps)")
        ax_gif.set_ylabel("Intensity")
        ax_gif.set_title(f"Pulse at z = {z[frame]:.1f} km")
        ax_gif.set_ylim(0, 1.1)
        ax_gif.grid(alpha=0.3)
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

# ── 导出 ──────────────────────────────────────────
st.markdown("---")
st.subheader("导出图片 / GIF / 视频")
if st.session_state.sponsor_valid:
    gif_fps = st.selectbox("GIF 速度 (fps)", [2, 4, 6, 12], index=2)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("导出 PNG 图片", use_container_width=True):
            from io import BytesIO
            buf_png = BytesIO()
            fig.savefig(buf_png, format="png", dpi=150, bbox_inches="tight")
            st.download_button(label="点击下载 PNG", data=buf_png.getvalue(), file_name="diagnostic_plot.png", mime="image/png", use_container_width=True)
    with col_b:
        if st.button("导出 GIF 动画", use_container_width=True):
            import matplotlib.animation as animation
            fig_anim, ax_anim = plt.subplots(figsize=(8, 5))
            n_frames = len(z)
            def update(frame):
                ax_anim.clear()
                ax_anim.plot(t, pulse[frame] / pulse[frame].max(), "r-", lw=2)
                ax_anim.set_xlabel("Time (ps)")
                ax_anim.set_ylabel("Normalized Intensity")
                ax_anim.set_title(f"z = {z[frame]:.1f} km")
                ax_anim.set_ylim(0, 1.1)
                ax_anim.grid(alpha=0.3)
            ani = animation.FuncAnimation(fig_anim, update, frames=n_frames, interval=80)
            fd2, gif_path2 = tempfile.mkstemp(suffix=".gif")
            os.close(fd2)
            ani.save(gif_path2, writer="pillow", fps=gif_fps)
            plt.close(fig_anim)
            with open(gif_path2, "rb") as g:
                gif_data = g.read()
            os.unlink(gif_path2)
            st.download_button(label="点击下载 GIF", data=gif_data, file_name="pulse_evolution.gif", mime="image/gif", use_container_width=True)
    st.markdown("---")
    st.markdown("感谢您的赞助支持！")
else:
    st.info("赞助后可解锁 PNG/GIF/MP4 导出功能")
    st.markdown("[去爱发电赞助](https://ifdian.net/a/S_Physics)")
# ── 实验说明 ──────────────────────────────────────────
st.subheader("物理说明")
if experiment == "高斯脉冲 GVD 展宽":
    st.markdown("""**物理本质**：高斯脉冲在单模光纤中传播时，群速度色散 (GVD) 导致不同频率分量以不同速度传播，脉冲被展宽。

**核心方程**（非线性薛定谪方程，纯色散情况）：
$$
\\frac{\\partial A}{\\partial z} = -i\\frac{\\beta_2}{2}\\frac{\\partial^2 A}{\\partial T^2}
$$

其中 $A(z,T)$ 为脉冲包络，$\\beta_2$ 为群速度色散系数，$T$ 为随脉冲移动的本地时间。

**解析解**（高斯脉冲初始条件 $A(0,T)=e^{-T^2/2T_0^2}$）：
$$
T(z) = T_0\\sqrt{1+(z/L_D)^2}, \\quad L_D = T_0^2/|\\beta_2|
$$

**关键观察**：
- 反常色散 ($\\beta_2<0$) 下脉冲展宽，频谱不变
- 展宽程度由色散长度 $L_D$ 决定
- 频谱宽度不变（线性过程）
""")
elif experiment == "啁啾脉冲压缩":
    st.markdown("""**物理本质**：带初始啁啾的脉冲在反常色散光纤中传播时，啁啾与色散相互作用导致脉冲先压缩后展宽。

**啁啾高斯脉冲**：
$$
A(0,T) = \\exp\\left(-\\frac{1+iC}{2}\\frac{T^2}{T_0^2}\\right)
$$

其中 $C$ 为啁啾参数。$C>0$ 表示前沿频率低、后沿频率高（正啁啾）。

**压缩条件**：当 $C\\beta_2<0$ （正啁啾 + 反常色散）时，脉冲先被压缩至最窄：
$$
z_{\\min} = \\frac{|C|}{1+C^2}L_D, \\quad T_{\\min} = \\frac{T_0}{\\sqrt{1+C^2}}
$$

**应用**：光通信中的色散补偿、激光脉冲压缩技术。
""")
elif experiment == "超高斯脉冲展宽":
    st.markdown("""**物理本质**：超高斯脉冲 ($m>1$) 具有更陡峭的边缘，其频谱展宽行为与标准高斯脉冲 ($m=1$) 显著不同。

**超高斯脉冲**：
$$
A(0,T) = \\exp\\left(-\\frac{1}{2}\\left|\\frac{T}{T_0}\\right|^{2m}\\right)
$$

其中 $m$ 为超高斯阶数：
- $m=1$ — 标准高斯脉冲（光滑边缘）
- $m=3$ — 近矩形脉冲（陡峭边缘）

**关键差异**：
- 超高斯脉冲边缘陡峭 → 频域分量更丰富
- GVD 导致边缘产生振荡结构
- 相比高斯脉冲，超高斯脉冲在相同距离下展宽更不均匀

**观察**：频谱图上出现的振荡结构是超高斯脉冲的特征指纹。
""")
elif experiment == "基态孤子 (N=1)":
    st.markdown("""**物理本质**：在反常色散光纤中，自相位调制 (SPM) 产生的非线性啁啾恰好补偿色散导致的脉冲展宽，形成稳定的孤子。

**非线性薛定谪方程**（含非线性项）：
$$
i\\frac{\\partial A}{\\partial z} = -\\frac{\\beta_2}{2}\\frac{\\partial^2 A}{\\partial T^2} + \\gamma |A|^2 A
$$

**基态孤子解**：
$$
A(z,T) = \\sqrt{P_0}\\,\\operatorname{sech}\\!\\left(\\frac{T}{T_0}\\right) e^{i\\gamma P_0 z/2}
$$

**孤子条件**（N=1）：
$$
N^2 = \\frac{\\gamma P_0 T_0^2}{|\\beta_2|} = 1 \\quad\\Rightarrow\\quad P_0 = \\frac{|\\beta_2|}{\\gamma T_0^2}
$$

**关键性质**：
- 孤子形状在传播中保持不变——色散与非线性精确平衡
- 孤子如同“光粒子”，可长距离传输信息
- 高阶孤子 (N>1) 呈现周期性呼吸行为
""")
