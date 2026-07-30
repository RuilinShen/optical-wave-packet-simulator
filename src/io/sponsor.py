import hashlib, json
from pathlib import Path
from datetime import datetime

CODES_FILE = Path(__file__).resolve().parent.parent.parent / "codes.json"

def _load():
    try:
        with open(CODES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def check_code(code, project=""):
    code = code.strip().upper()
    h = hashlib.sha256(code.encode()).hexdigest()
    for c in _load():
        if c["hash"] == h:
            if not c.get("active", True):
                return {"valid": False, "message": "\u8d5e\u52a9\u7801\u5df2\u7981\u7528"}
            if project and c.get("project") and c["project"] != project:
                return {"valid": False, "message": "\u8d5e\u52a9\u7801\u4e0d\u5c5e\u4e8e\u6b64\u9879\u76ee"}
            exp = c.get("expires")
            if exp:
                try:
                    if datetime.fromisoformat(exp) < datetime.now():
                        return {"valid": False, "message": "\u8d5e\u52a9\u7801\u5df2\u8fc7\u671f"}
                except:
                    pass
            return {"valid": True, "tier": c.get("tier", "full"), "expires_at": exp}
    return {"valid": False, "message": "\u8d5e\u52a9\u7801\u65e0\u6548"}

def get_sponsor_status(code):
    r = check_code(code)
    if r.get("valid"):
        exp = r.get("expires_at", "")
        msg = f"\u5df2\u89e3\u9501\uff08\u6709\u6548\u671f\u81f3 {exp}\uff09" if exp else "\u5df2\u89e3\u9501\uff08\u6c38\u4e45\u6709\u6548\uff09"
        return (True, msg)
    return (False, r.get("message", "\u8d5e\u52a9\u7801\u65e0\u6548"))

# \u4fdd\u6301\u517c\u5bb9
get_license_state = lambda: {"tier": "trial", "valid": False, "expires_at": None}
