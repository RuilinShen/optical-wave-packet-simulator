#!/usr/bin/env python3
import hashlib, json, uuid, sys, os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
CODES_FILE1 = os.path.join(BASE, "..", "codes.json")
CODES_FILE2 = os.path.join(BASE, "..", "..", "CHAOS_DIR", "codes.json")
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

def save_codes(codes, raw_code=""):
    with open(CODES_FILE1, "w", encoding="utf-8") as f:
        json.dump(codes, f, indent=2, ensure_ascii=False)
    if raw_code:
        h = hashlib.sha256(raw_code.encode()).hexdigest()
        s = load_secrets()
        s[h] = raw_code
        try:
            with open(SECRET_FILE, "w", encoding="utf-8") as f:
                json.dump(s, f, indent=2, ensure_ascii=False)
        except:
            pass
    try:
        d2 = os.path.dirname(CODES_FILE2)
        if d2:
            os.makedirs(d2, exist_ok=True)
        with open(CODES_FILE2, "w", encoding="utf-8") as f:
            json.dump(codes, f, indent=2, ensure_ascii=False)
        print(" [sync: chaos ok]")
    except:
        print(" [sync: chaos FAILED]")

def gen(project, owner, days):
    raw = "SPONSOR-" + uuid.uuid4().hex[:8].upper()
    h = hashlib.sha256(raw.encode()).hexdigest()
    exp = (datetime.now() + timedelta(days=days)).isoformat()[:10] if days > 0 else None
    codes = load_codes()
    codes.append({"hash": h, "project": project, "owner": owner,
        "tier": "full", "created": datetime.now().isoformat()[:10],
        "expires": exp, "active": True})
    save_codes(codes, raw)
    print("[OK] Code: " + raw)
    print("      Project:", project, " Owner:", owner, " Expires:", exp or "forever")
    return raw

def list_codes():
    codes = load_codes()
    sec = load_secrets()
    if not codes:
        print("No codes.")
        return
    from datetime import datetime
    print(" # ST PROJECT   OWNER     REMAIN     EXPIRES      CODE")
    print("-" * 65)
    for i, c in enumerate(codes):
        st = "V" if c.get("active") else "X"
        p = c.get("project", "")
        o = c.get("owner", "")
        exp = c.get("expires")
        if exp:
            try:
                rem_d = (datetime.fromisoformat(exp) - datetime.now()).days
                rem = str(rem_d) + "d" if rem_d >= 0 else "expired"
            except:
                rem = exp[:10]
        else:
            rem = "forever"
        e = exp or "forever"
        r = sec.get(c.get("hash",""), "")
        print(f"{i+1:>2} {st:>2} {p:>9} {o:>8} {rem:>7} {e:>11} {r}")

def extend(n, days):
    codes = load_codes()
    if 1 <= n <= len(codes):
        codes[n-1]["expires"] = (datetime.now() + timedelta(days=days)).isoformat()[:10]
        codes[n-1]["active"] = True
        save_codes(codes)
        print("[OK] Extended #" + str(n) + " -> " + codes[n-1]["expires"])
    else:
        print("[ERR] Invalid")

def delete_codes(n):
    codes = load_codes()
    if 1 <= n <= len(codes):
        r = codes.pop(n-1)
        save_codes(codes)
        print("[OK] Deleted #" + str(n) + " (" + r.get("owner","") + ")")
    else:
        print("[ERR] Invalid")

def toggle(n, active):
    codes = load_codes()
    if 1 <= n <= len(codes):
        codes[n-1]["active"] = active
        save_codes(codes)
        print("[OK] " + ("Enabled" if active else "Disabled") + " #" + str(n))
    else:
        print("[ERR] Invalid")

if __name__ == "__main__":
    def usage():
        print("Commands: gen  list  disable N  enable N  extend N DAYS  delete N")
    if len(sys.argv) < 2:
        usage(); sys.exit(1)
    c = sys.argv[1]
    try:
        if c == "gen":
            gen(input("Project (optical/chaos): ").strip(),
                input("Owner: ").strip(),
                int(input("Days (0=forever): ").strip() or "30"))
        elif c == "list":
            list_codes()
        elif c == "disable":
            toggle(int(sys.argv[2] if len(sys.argv)>2 else input("N: ")), False)
        elif c == "enable":
            toggle(int(sys.argv[2]) if len(sys.argv)>2 else int(input("N: ")), True)
        elif c == "extend":
            n = int(sys.argv[2]) if len(sys.argv)>2 else int(input("N: "))
            d = int(sys.argv[3]) if len(sys.argv)>3 else int(input("Days: "))
            extend(n, d)
        else:
            print("Unknown:", c); usage()
    except Exception as e:
        print("[ERROR]", e)
