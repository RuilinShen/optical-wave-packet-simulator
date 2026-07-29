import sys
with open("app.py","r",encoding="utf-8") as f:
    lines = f.readlines()
# 1. Remove fixed defaults from L2 viz section (line ~201)
for i,l in enumerate(lines):
    if "wvl = 633e-9" in l and "w0" not in l:
        lines[i] = ""; lines[i+1] = ""; lines[i+2] = ""
        break
# 2. Make 4-panel plot and GIF conditional on L1 experiments
L1 = ['"\u9ad8\u65af\u8109\u51b2 GVD \u5c55\u5bbd"','"\u5531\u5549\u8109\u51b2\u538b\u7f29"','"\u8d85\u9ad8\u65af\u8109\u51b2\u5c55\u5bbd"','"\u4e09\u9636\u8272\u6563 (TOD)"','"\u57fa\u6001\u5b64\u5b50 (N=1)"','"\u9ad8\u9636\u5b64\u5b50 (N>1)"']
cond = "if experiment in (" + ",".join(L1) + "):\n"
for i,l in enumerate(lines):
    if '# \u2500\u2500 \u56fe' in l:
        lines.insert(i, cond)
        break
for i,l in enumerate(lines):
    if l.strip().startswith('st.subheader("') and i > 180:
        lines.insert(i, "\n")
        break
# 3. Expand L2 physics descriptions with formulas
for i,l in enumerate(lines):
    if 'elif experiment == "\u7a7a\u95f4\u5149\u675f\u8854\u5c04":' in l:
        lines[i+1] = '    st.markdown("\u9ad8\u65af\u5149\u675f\u5728\u81ea\u7531\u7a7a\u95f4\u4e2d\u4f20\u64ad\u65f6\u56e0\u8854\u5c04\u800c\u9010\u6e10\u5c55\u5bbd\u3002\u89d2\u8c31\u6cd5\uff1a$E(x,y,z)=F^{-1}[F(E_0)\\cdot e^{ik_zz}]$ \uff0c\u5176\u4e2d $k_z=\\\\sqrt{k^2-k_x^2-k_y^2}$ \u3002\u675f\u8170\u8d8a\u5c0f\u3001\u6ce2\u957f\u8d8a\u957f\uff0c\u8854\u5c04\u8d8a\u660e\u663e\u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "HG/LG \u6a21\u5f0f":' in l:
        lines[i+1] = '    st.markdown("\u5c3c\u7c73-\u9ad8\u65af\uff1a$HG_{mn}(x,y)=C_{mn}H_m(\\\\sqrt{2}x/w)H_n(\\\\sqrt{2}y/w)e^{-(x^2+y^2)/w^2}$ \u3002\u62c9\u76d6\u5c14-\u9ad8\u65af\uff1a$LG_{pl}(r,\\\\theta)=C_{pl}(\\\\sqrt{2}r/w)^{|l|}L_p^{|l|}(2r^2/w^2)e^{-r^2/w^2}e^{-il\\\\theta}$ \u3002LG\u542b\u6da1\u65cb\u76f8\u4f4d$e^{-il\\\\theta}$\uff0c\u643a\u5e26\u8f68\u9053\u89d2\u52a8\u91cf\u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "\u5927\u6c14\u6d79\u6d41":' in l:
        lines[i+1] = '    st.markdown("Kolmogorov \u6d79\u6d41\u8c31\uff1a$\\\\Phi(k)=0.023\\\\,r_0^{-5/3}k^{-11/3}$ \u3002$r_0$ \u4e3aFried\u53c2\u6570\uff0c\u8861\u91cf\u6d79\u6d41\u5f3a\u5ea6\u3002\u76f8\u4f4d\u5c4f\u901a\u8fc7\u5085\u91cc\u53f6\u53cd\u6f14\u751f\u6210\uff0c\u6a21\u62df\u5927\u6c14\u968f\u673a\u7578\u53d8\u5bfc\u81f4\u7684\u5149\u675f\u5c55\u5bbd\u548c\u95ea\u70c1\u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "\u504f\u632f\u6f14\u5316":' in l:
        lines[i+1] = '    st.markdown("Jones\u5411\u91cf\uff1a$J=\\\\begin{bmatrix}E_x\\\\\\\\E_y\\\\end{bmatrix}$ \u3002Stokes\u53c2\u6570\uff1a$S_0=|E_x|^2+|E_y|^2,\\\\,S_1=|E_x|^2-|E_y|^2,\\\\,S_2=2\\\\Re(E_xE_y^*),\\\\,S_3=2\\\\Im(E_xE_y^*)$ \u3002\u53cc\u6298\u5c04\u4ecb\u8d28\u4e2d\uff0c\u4e24\u504f\u632f\u5206\u91cf\u7ecf\u5386\u4e0d\u540c\u76f8\u4f4d$\\\\Delta\\\\phi=2\\\\pi\\\\Delta n L/\\\\lambda$\u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "XPM (\u4ea4\u53c9\u76f8\u4f4d\u8c03\u5236)":' in l:
        lines[i+1] = '    st.markdown("\u975e\u7ebf\u6027\u859b\u5b9a\u8c2a\u65b9\u7a0b\uff08XPM\uff09\uff1a$\\\\partial_{z}A_1=-i\\\\beta_2/2\\\\cdot\\\\partial_T^2A_1+i\\\\gamma(|A_1|^2+2|A_2|^2)A_1$\uff0c$\\\\partial_{z}A_2=-i\\\\beta_2/2\\\\cdot\\\\partial_T^2A_2+i\\\\gamma(|A_2|^2+2|A_1|^2)A_2$ \u3002\u5176\u4e2d\u7cfb\u6570\u201c2\u201d\u4e3aXPM\u7279\u5f81\uff0c\u5373A1\u7684\u975e\u7ebf\u6027\u76f8\u4f4d\u53d7A2\u5f71\u54cd\u7a0b\u5ea6\u662f\u81ea\u8eabSPM\u7684\u4e24\u500d\u3002")\n')
        break
with open("app.py","w",encoding="utf-8") as f:
    f.writelines(lines)
try:
    compile(open("app.py",encoding="utf-8").read(),"app.py","exec")
    print("OK")
except SyntaxError as e:
    print(f"Error line {e.lineno}")
import os; os.remove("_fix_remaining.py")
