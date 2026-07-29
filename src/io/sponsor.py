"""赞助验证客户端 — 零依赖版"""
import json, os
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

# 验证服务器地址（部署后替换）
VALIDATION_SERVER = "http://localhost:5000"
CACHE_DIR = Path(__file__).parent.parent.parent / ".license_cache"
CACHE_FILE = CACHE_DIR / "license.json"

def _api(path, data=None):
    """调用验证服务器的 API"""
    url = VALIDATION_SERVER + path
    body = json.dumps(data).encode() if data else None
    try:
        req = Request(url, body, {"Content-Type": "application/json"})
        with urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except (URLError, OSError):
        return None

def _load_cache():
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def _save_cache(data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def check_code(code):
    """验证赞助码，先试服务器，失败回退本地缓存"""
    code = code.strip().upper()
    if not code.startswith("SPONSOR-"):
        return {"valid": False, "message": "赞助码格式不正确"}

    # 服务器验证
    result = _api("/validate", {"code": code})
    if result:
        if result.get("valid"):
            _save_cache({"code": code, "tier": result.get("tier", "full"),
                        "expires_at": result.get("expires_at"),
                        "cached_at": datetime.now().isoformat()})
        return result

    # 回退缓存
    cache = _load_cache()
    if cache.get("code") == code:
        expires = cache.get("expires_at")
        if expires:
            try:
                if datetime.fromisoformat(expires) >= datetime.now():
                    return {"valid": True, "tier": cache.get("tier", "full"), "expires_at": expires}
            except:
                pass
        else:
            return {"valid": True, "tier": cache.get("tier", "full")}
    
    return {"valid": False, "message": "无法连接验证服务器，请检查网络"}

def get_sponsor_status(code):
    """保持现有接口兼容 — 返回 (bool, str)"""
    result = check_code(code)
    if result.get("valid"):
        expires = result.get("expires_at", "")
        msg = f"已解锁（有效期至 {expires}）" if expires else "已解锁（永久有效）"
        return (True, msg)
    return (False, result.get("message", "赞助码无效"))

def get_license_state():
    """获取当前许可证状态，用于启动时判断"""
    cache = _load_cache()
    code = cache.get("code", "")
    if not code:
        return {"tier": "trial", "valid": False, "expires_at": None}

    # 定期重新验证
    result = _api("/check", {"code": code})
    if result:
        if result.get("valid"):
            return {"tier": result.get("tier", "full"), "valid": True,
                    "expires_at": result.get("expires_at")}
        _save_cache({})  # 失效则清除
        return {"tier": "trial", "valid": False, "expires_at": None}

    # 回退缓存
    expires = cache.get("expires_at")
    if expires:
        try:
            if datetime.fromisoformat(expires) >= datetime.now():
                return {"tier": cache.get("tier", "full"), "valid": True, "expires_at": expires}
        except:
            pass
    return {"tier": "trial", "valid": False, "expires_at": None}
