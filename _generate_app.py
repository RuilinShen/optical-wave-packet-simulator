import sys
with open("app.py","r",encoding="utf-8") as f:
    lines = f.readlines()
# Keep the first 10 lines (header and imports up to plot_evolution import)
header = lines[:29]
header.append('st.markdown("""<div style=\'position:fixed;top:0;left:0;width:100%;height:100%;z-index:2147483647;pointer-events:none;background-image:url(\\"data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27300%27 height=%27300%27%3E%3Ctext x=%27150%27 y=%27120%27 font-size=%2720%27 fill=%27%23999%27 fill-opacity=%270.15%27 transform=%27rotate(-30,150,150)%27 text-anchor=%27middle%27 font-family=%27Arial%27%3Eifdian.net/a/S_Physics%3C/text%3E%3Ctext x=%27150%27 y=%27180%27 font-size=%2714%27 fill=%27%23999%27 fill-opacity=%270.15%27 transform=%27rotate(-30,150,150)%27 text-anchor=%27middle%27 font-family=%27Arial%27%3Egithub.com/RuilinShen%3C/text%3E%3C/svg%3E\\");background-repeat:repeat;\'></div>""", unsafe_allow_html=True)\n')
header.append('st.title("\\u5149\\u5b66\\u6ce2\\u5305\\u5168\\u5b9e\\u9a8c\\u6a21\\u62df\\u5668")\n')
header.append('st.markdown("\\u4ea4\\u4e92\\u5f0f\\u4eff\\u771f\\u5e73\\u53f0 \\u2014\\u2014 \\u8c03\\u8282\\u53c2\\u6570\\uff0c\\u5373\\u65f6\\u89c2\\u5bdf\\u8109\\u51b2\\u5728\\u5149\\u7ea4\\u4e2d\\u7684\\u4f20\\u64ad\\u4e0e\\u6f14\\u5316\\u3002")\n')
print("Header saved:", len(header))
import os; os.remove("_generate_app.py")
