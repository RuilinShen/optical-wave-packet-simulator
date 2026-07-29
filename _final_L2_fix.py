import sys
with open("app.py","r",encoding="utf-8") as f:
    lines = f.readlines()
L2_EXPS = '("\u7a7a\u95f4\u5149\u675f\u8852\u5c04","HG/LG \u6a21\u5f0f","\u5927\u6c14\u6e6d\u6d41","\u504f\u632f\u6f14\u5316","XPM (\u4ea4\u53c9\u76f8\u4f4d\u8c03\u5236)")'
cond = "if experiment not in " + L2_EXPS + ":\n"
# Find 4-panel plot and wrap
for i,l in enumerate(lines):
    if 'plt.subplots(2, 2' in l:
        lines.insert(i, cond)
        start = i + 1
        break
for i,l in enumerate(lines):
    if 'st.pyplot(fig)' in l and i > start:
        # Indent lines from start to i
        for j in range(start, i+1):
            if lines[j].strip():
                lines[j] = '    ' + lines[j]
        break
for i,l in enumerate(lines):
    if 'animation.FuncAnimation' in l:
        start2 = i
        # Insert condition before this line
        lines.insert(i, cond)
        start2 = i + 1
        break
for i,l in enumerate(lines):
    if "st.error(f" in l and i > start2 and "GIF" in l:
        for j in range(start2, i+1):
            if lines[j].strip():
                lines[j] = '    ' + lines[j]
        break
# Expand L2 physics descriptions
for i,l in enumerate(lines):
    if 'elif experiment == "\u7a7a\u95f4\u5149\u675f\u8852\u5c04":' in l:
        lines[i+1] = '    st.markdown("\u89d2\u8c31\u6cd5\uff1a$E(x,y,z)=F^{-1}[F(E_0)e^{ik_zz}]$\uff0c$k_z=\\\sqrt{k^2-k_x^2-k_y^2}$ \u3002\u675f\u8170\u8d8a\u5c0f\u3001\u6ce2\u957f\u8d8a\u957f\uff0c\u8852\u5c04\u8d8a\u660e\u663e\u3002\u8852\u5c04\u957f\u5ea6$L_D=kw_0^2/2$\u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "HG/LG \u6a21\u5f0f":' in l:
        lines[i+1] = '    st.markdown("HG$_{mn}$\uff1a$H_m(\\sqrt{2}x/w)H_n(\\sqrt{2}y/w)e^{-r^2/w^2}$ \u3002LG$_{pl}$\uff1a$(\\sqrt{2}r/w)^{|l|}L_p^{|l|}(2r^2/w^2)e^{-r^2/w^2}e^{-il\\\\theta}$ \u3002LG\u542b\u6da1\u65cb\u76f8\u4f4d$e^{-il\\\\theta}$\uff0c\u643a\u5e26\u8f68\u9053\u89d2\u52a8\u91cf\u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "\u5927\u6c14\u6e6d\u6d41":' in l:
        lines[i+1] = '    st.markdown("Kolmogorov\u6d79\u6d41\u8c31\uff1a$\\\\Phi_n(k)=0.033C_n^2k^{-11/3}$ \u3002Fried\u53c2\u6570$r_0=(0.423k^2C_n^2\\\\Delta z)^{-3/5}$ \u3002\u76f8\u4f4d\u5c4f\u901a\u8fc7\u5085\u91cc\u53f6\u53cd\u6f14\u751f\u6210\uff0c\u6a21\u62df\u968f\u673a\u7578\u53d8\u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "\u504f\u632f\u6f14\u5316":' in l:
        lines[i+1] = '    st.markdown("Jones\u5411\u91cf$J=[E_x,E_y]^T$ \u3002Stokes\u53c2\u6570$S_0=|E_x|^2+|E_y|^2$,$S_1=|E_x|^2-|E_y|^2$,$S_2=2\\\\Re(E_xE_y^*)$,$S_3=2\\\\Im(E_xE_y^*)$ \u3002\u53cc\u6298\u5c04\u76f8\u4f4d\u5ef6\u8fdf$\\\\Delta\\\\phi=2\\\\pi\\\\Delta nL/\\\\lambda$ \u3002")\n')
        break
for i,l in enumerate(lines):
    if 'elif experiment == "XPM (\u4ea4\u53c9\u76f8\u4f4d\u8c03\u5236)":' in l:
        lines[i+1] = '    st.markdown("\u8026\u5408NLSE\uff1a$i\\\\partial_zA_1=-\\\\beta_2/2\\\\cdot\\\\partial_T^2A_1+\\\\gamma(|A_1|^2+2|A_2|^2)A_1$ \u3002\u7cfb\u6570\u201c2\u201d\u4e3aXPM\u7279\u5f81\u3002")\n')
        break
with open("app.py","w",encoding="utf-8") as f:
    f.writelines(lines)
try:
    compile(open("app.py",encoding="utf-8").read(),"app.py","exec")
    print("OK")
except SyntaxError as e:
    print(f"Error line {e.lineno}")
import os; os.remove("_final_L2_fix.py")
