import sys
with open("app.py","r",encoding="utf-8") as f:
    lines = f.readlines()
# Fix the broken sidebar control (lines 103-105)
lines[102] = "if experiment in (\u201c\u57fa\u6001\u5b64\u5b50 (N=1)\u201d, \u201c\u9ad8\u9636\u5b64\u5b50 (N>1)\u201d):\n"
del lines[103:105]
# Fix the broken elif in physics description (search for it)
for i, line in enumerate(lines):
    if "if experiment == \"\u4e09\u9636\u8272\u6563" in line and "TOD" in lines[i+4]:
        # This is the sidebar section, not the description - skip
        continue
    if "\"if\" experiment == "\u4e09\u9636\u8272\u6563" in line or "experiment == \"\u4e09\u9636\u8272\u6563" in line:
        # Check if this is the description section (has st.markdown nearby)
        content = "".join(lines[i:i+10])
        if "st.markdown" in content and "\u7269\u7406" not in content:
            lines[i] = "elif experiment == \"\u57fa\u6001\u5b64\u5b50 (N=1)\":\n"
            break
with open("app.py","w",encoding="utf-8") as f:
    f.writelines(lines)
try:
    compile(open("app.py",encoding="utf-8").read(),"app.py","exec")
    print("Syntax OK")
except SyntaxError as e:
    print(f"Syntax error: {e.text}")
import os; os.remove("_fix_corrupt.py")
