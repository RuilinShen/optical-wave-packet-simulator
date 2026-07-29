import sys
with open("app.py","r",encoding="utf-8") as f:
    lines = f.readlines()
# Find description section boundaries
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if '\u2500\u2500 \u7269\u7406\u8bf4\u660e' in line:
        start_idx = i + 2  # skip the comment and subheader lines
    if 'st.caption(' in line and start_idx > 0:
        end_idx = i
        break
new_desc = []
def add(title, first_eq, second_eq, obs):
    new_desc.append('if experiment == "' + title + '":\n')
    new_desc.append('    st.markdown(first_eq.replace("|","\\n"))\n')
    new_desc.append('    st.latex(r"' + second_eq + '")\n')
    new_desc.append('    st.markdown(obs.replace("|","\\n"))\n')
# But we can't use dynamic code easily. Let me write directly.
new_desc = []
# GVD
new_desc.append('if experiment == "\u9ad8\u65af\u8109\u51b2 GVD \u5c55\u5bbd":\n')
new_desc.append('    st.markdown("**\u7269\u7406\u672c\u8d28**\uff1a\u9ad8\u65af\u8109\u51b2\u5728\u5355\u6a21\u5149\u7ea4\u4e2d\u4f20\u64ad\u65f6\uff0c\u7fa4\u901f\u5ea6\u8272\u6563 (GVD) \u5bfc\u81f4\u4e0d\u540c\u9891\u7387\u5206\u91cf\u4ee5\u4e0d\u540c\u901f\u5ea6\u4f20\u64ad\uff0c\u8109\u51b2\u88ab\u5c55\u5bbd\u3002")\n')
new_desc.append('    st.markdown("**\u6838\u5fc3\u65b9\u7a0b**\uff1a\u7ebf\u6027\u859b\u5b9a\u8c2a\u65b9\u7a0b")\n')
new_desc.append('    st.latex(r"\\\\frac{\\\\partial A}{\\\\partial z} = -i\\\\frac{\\\\beta_2}{2}\\\\frac{\\\\partial^2 A}{\\\\partial T^2}")\n')
new_desc.append('    st.markdown("**\u89e3\u6790\u89e3**\uff1a$T(z)=T_0\\\\sqrt{1+(z/L_D)^2}$\uff0c\u5176\u4e2d $L_D=T_0^2/|\\\\beta_2|$ \u4e3a\u8272\u6563\u957f\u5ea6\u3002")\n')
new_desc.append('    st.markdown("**\u5173\u952e\u89c2\u5bdf**\uff1a\u53cd\u5e38\u8272\u6563 ($\\\\beta_2<0$) \u4e0b\u8109\u51b2\u5c55\u5bbd\uff0c\u9891\u8c31\u4e0d\u53d8\u3002$L_D$ \u8d8a\u5c0f\u5c55\u5bbd\u8d8a\u5feb\u3002")\n')
# Chirped
new_desc.append('elif experiment == "\u5531\u5549\u8109\u51b2\u538b\u7f29":\n')
new_desc.append('    st.markdown("**\u7269\u7406\u672c\u8d28**\uff1a\u5e26\u521d\u59cb\u5531\u5549\u7684\u8109\u51b2\u5728\u53cd\u5e38\u8272\u6563\u5149\u7ea4\u4e2d\u4f20\u64ad\u65f6\uff0c\u5531\u5549\u4e0e\u8272\u6563\u76f8\u4e92\u4f5c\u7528\u5bfc\u81f4\u8109\u51b2\u5148\u538b\u7f29\u540e\u5c55\u5bbd\u3002")\n')
new_desc.append('    st.markdown("**\u5531\u5549\u9ad8\u65af\u8109\u51b2**\uff1a$A(0,T)=\\\\exp[-(1+iC)T^2/2T_0^2]$")\n')
new_desc.append('    st.latex(r"z_{\\\\min} = \\\\frac{|C|}{1+C^2}L_D, \\\\quad T_{\\\\min} = \\\\frac{T_0}{\\\\sqrt{1+C^2}}")\n')
new_desc.append('    st.markdown("**\u5e94\u7528**\uff1a\u5149\u901a\u4fe1\u4e2d\u7684\u8272\u6563\u8865\u507f\u3001\u6fc0\u5149\u8109\u51b2\u538b\u7f29\u6280\u672f\u3002\u5f53 $C\\\\beta_2<0$\u65f6\u538b\u7f29\u6700\u663e\u8457\u3002")\n')
# Super-Gaussian
new_desc.append('elif experiment == "\u8d85\u9ad8\u65af\u8109\u51b2\u5c55\u5bbd":\n')
new_desc.append('    st.markdown("**\u7269\u7406\u672c\u8d28**\uff1a\u8d85\u9ad8\u65af\u8109\u51b2 ($m>1$) \u8fb9\u7f18\u66f4\u9661\u5ced\uff0c\u5176\u9891\u8c31\u5c55\u5bbd\u884c\u4e3a\u4e0e\u6807\u51c6\u9ad8\u65af ($m=1$) \u663e\u8457\u4e0d\u540c\u3002")\n')
new_desc.append('    st.markdown("**\u8d85\u9ad8\u65af\u8109\u51b2**\uff1a$A(0,T)=\\\\exp(-\\\\frac12|T/T_0|^{2m})$")\n')
new_desc.append('    st.markdown("**\u5173\u952e\u5dee\u5f02**\uff1a\u8d85\u9ad8\u65af\u8109\u51b2\u8fb9\u7f18\u9661\u5ced\u2192\u9891\u57df\u5206\u91cf\u66f4\u4e30\u5bcc\uff1bGVD \u5bfc\u81f4\u8fb9\u7f18\u4ea7\u751f\u632f\u8361\u7ed3\u6784\u3002 $m$ \u8d8a\u5927\u632f\u8361\u8d8a\u660e\u663e\u3002")\n')
# TOD
new_desc.append('elif experiment == "\u4e09\u9636\u8272\u6563 (TOD)":\n')
new_desc.append('    st.markdown("**\u7269\u7406\u672c\u8d28**\uff1a\u4e09\u9636\u8272\u6563 ($\\\\beta_3$) \u5bfc\u81f4\u8109\u51b2\u975e\u5bf9\u79f0\u7578\u53d8\uff0c\u4ea7\u751f\u632f\u8361\u7ed3\u6784\u3002\u5bf9\u4e8e\u8d85\u77ed\u8109\u51b2 ($T_0<1$ ps) \u4e0d\u53ef\u5ffd\u7565\u3002")\n')
new_desc.append('    st.markdown("**\u9891\u57df\u76f8\u4f4d**\uff1a$\\\\phi(\\\\omega)=\\\\beta_2\\\\omega^2/2 + \\\\beta_3\\\\omega^3/6$")\n')
new_desc.append('    st.markdown("**\u89c2\u5bdf**\uff1a$\\\\beta_3>0$ \u5728\u524d\u6cbf\u4ea7\u751f\u632f\u8361\uff0c$\\\\beta_3<0$ \u5728\u540e\u6cbf\u4ea7\u751f\u632f\u8361\u3002\u6b63\u8d1f\u53ef\u901a\u8fc7\u53c2\u6570\u6ed1\u5757\u8c03\u6574\u3002")\n')
# Fundamental soliton
new_desc.append('elif experiment == "\u57fa\u6001\u5b64\u5b50 (N=1)":\n')
new_desc.append('    st.markdown("**\u7269\u7406\u672c\u8d28**\uff1a\u53cd\u5e38\u8272\u6563\u4e0e\u81ea\u76f8\u4f4d\u8c03\u5236 (SPM) \u7cbe\u786e\u5e73\u8861\uff0c\u5f62\u6210\u7a33\u5b9a\u7684\u5b64\u5b50\u3002")\n')
new_desc.append('    st.markdown("**\u975e\u7ebf\u6027\u859b\u5b9a\u8c2a\u65b9\u7a0b**\uff1a")\n')
new_desc.append('    st.latex(r"i\\\\frac{\\\\partial A}{\\\\partial z} = -\\\\frac{\\\\beta_2}{2}\\\\frac{\\\\partial^2 A}{\\\\partial T^2} + \\\\gamma |A|^2 A")\n')
new_desc.append('    st.markdown("**\u5b64\u5b50\u6761\u4ef6**\uff1a$N^2=\\\\gamma P_0 T_0^2/|\\\\beta_2|=1$ \u2192 $P_0=|\\\\beta_2|/(\\\\gamma T_0^2)$")\n')
new_desc.append('    st.markdown("**\u6027\u8d28**\uff1a\u5b64\u5b50\u5f62\u72b6\u5728\u4f20\u64ad\u4e2d\u4fdd\u6301\u4e0d\u53d8\uff0c\u5982\u540c\u201c\u5149\u7c92\u5b50\u201d\u3002\u53ef\u957f\u8ddd\u79bb\u4f20\u8f93\u4fe1\u606f\u3002")\n')
# Higher-order soliton
new_desc.append('elif experiment == "\u9ad8\u9636\u5b64\u5b50 (N>1)":\n')
new_desc.append('    st.markdown("**\u7269\u7406\u672c\u8d28**\uff1a$N>1$ \u65f6\u5b64\u5b50\u5448\u73b0\u5468\u671f\u6027\u547c\u5438\u884c\u4e3a\u2014\u2014\u8109\u51b2\u5468\u671f\u6027\u538b\u7f29\u3001\u5206\u88c2\u3001\u6062\u590d\u3002")\n')
new_desc.append('    st.markdown("**\u5468\u671f**\uff1a$z_0 = \\\\pi L_D/2$")\n')
new_desc.append('    st.markdown("**\u89c2\u5bdf**\uff1a$N=2$ \u65f6\u8109\u51b2\u5728\u534a\u4e2a\u5468\u671f\u5904\u6700\u7a84\uff0c\u7136\u540e\u5206\u88c2\u4e3a\u53cc\u5cf0\u3002$N$ \u8d8a\u5927\u547c\u5438\u8d8a\u5267\u70c8\u3002\u53c2\u6570\u6ed1\u5757\u53ef\u8c03\u8282 $N$ \u503c\u3002")\n')
# Replace the description section
lines[start_idx:end_idx] = new_desc
with open("app.py","w",encoding="utf-8") as f:
    f.writelines(lines)
try:
    compile(open("app.py",encoding="utf-8").read(),"app.py","exec")
    print("Syntax OK")
except SyntaxError as e:
    print(f"Error at line {e.lineno}: {e.text}")
import os; os.remove("_new_descriptions.py")
