#!/usr/bin/env python3
"""赞助码管理工具 - 本地生成和管理赞助码"""
import hashlib, json, uuid, sys, os
from datetime import datetime, timedelta

# 光学模拟器目录
BASE = os.path.dirname(os.path.abspath(__file__))
CODES_FILE1 = os.path.join(BASE, "..", "codes.json")
CODES_FILE2 = os.path.join(BASE, "..", "..", "混沌摆模拟器逐步教学/chaos-pendulum", "codes.json")
SECRET_FILE = os.path.join(BASE, "..", ".codes_secret.json")

def load_codes():
    try:
        with open(CODES_FILE1, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def load_secrets():
    try:
        with open(SECRET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_codes(codes):
    with open(CODES_FILE1, "w", encoding="utf-8") as f:
        json.dump(codes, f, indent=2, ensure_ascii=False)
    # 同步写入混沌摆
    try:
        d2 = os.path.dirname(CODES_FILE2)
        if d2:
            os.makedirs(d2, exist_ok=True)
        with open(CODES_FILE2, "w", encoding="utf-8") as f:
            json.dump(codes, f, indent=2, ensure_ascii=False)
        print("  (已同步写入混沌摆目录)")
    except:
        print("  (警告: 无法写入混沌摆目录)")

def gen(project, owner, days, tier="full"):
    raw = "SPONSOR-" + uuid.uuid4().hex[:8].upper()
    h = hashlib.sha256(raw.encode()).hexdigest()
    exp = (datetime.now() + timedelta(days=days)).isoformat()[:10] if days > 0 else None
    codes = load_codes()
    codes.append({
        "hash": h, "project": project, "owner": owner,
        "tier": tier, "created": datetime.now().isoformat()[:10],
        "expires": exp, "active": True
    })
    save_codes(codes)
    print(f"\u2714 \u751f\u6210\u6210\u529f\uff01\u8d5e\u52a9\u7801: {raw}")
    print(f"  \u9879\u76ee: {project}  \u5f52\u5c5e: {owner}  \u6709\u6548\u671f: {exp or '\u6c38\u4e45'}")
    return raw

def list_codes():
    codes = load_codes()
    secrets = load_secrets()
    if not codes:
        print("\u6682\u65e0\u8d5e\u52a9\u7801")
        return
    print(f"{'#':>3} {'V/X':>4} {'\u9879\u76ee':>10} {'\u5f52\u5c5e':>8} {'\u5230\u671f':>12} {'\u8d5e\u52a9\u7801':>20}")
    print("-" * 65)
    for i, c in enumerate(codes):
        st = "V" if c.get("active") else "X"
        p = c.get("project", "")
        o = c.get("owner", "")
        e = c.get("expires", "\u6c38\u4e45") or "\u6c38\u4e45"
        raw = secrets.get(c.get("hash",""), "")
        print(f"{i+1:>3} {st:>4} {p:>10} {o:>8} {e:>12} {raw:>20}")

def toggle(index, active):
    codes = load_codes()
    if 1 <= index <= len(codes):
        codes[index-1]["active"] = active
        save_codes(codes)
        print(f"\u2714 \u5df2{'\u542f\u7528' if active else '\u7981\u7528'}\u7b2c {index} \u4e2a\u8d5e\u52a9\u7801")
    else:
        print("\u2718 \u7f16\u53f7\u65e0\u6548")

if __name__ == "__main__":
    cmds = {"gen": "\u751f\u6210新码", "list": "\u5217出所有码",
            "disable": "\u7981用 #", "enable": "\u542f用 #"}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print("\u7528\u6cd5: python manage_codes.py <\u547d\u4ee4>")
        for k, v in cmds.items():
            print(f"  {k:8} {v}")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "gen":
        p = input("\u9879\u76ee (optical/chaos): ").strip()
        o = input("\u5f52\u5c5e\u4eba: ").strip()
        d = int(input("\u6709\u6548\u671f\u5929\u6570 (0=\u6c38\u4e45): ").strip() or "30")
        gen(p, o, d)
    elif cmd == "list":
        list_codes()
    elif cmd in ("disable", "enable"):
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else int(input("\u7f16\u53f7: ").strip())
        toggle(idx, cmd == "enable")
