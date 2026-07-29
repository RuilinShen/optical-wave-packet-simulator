import json, sqlite3, uuid, os
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from datetime import datetime, timedelta

DB = os.path.join(os.path.dirname(__file__), "licenses.db")
ADMIN_SECRET = "admin_oqp38se2"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS licenses (
        code TEXT PRIMARY KEY, tier TEXT DEFAULT "full",
        created_at TEXT, expires_at TEXT,
        max_uses INTEGER DEFAULT 0, uses INTEGER DEFAULT 0,
        last_used TEXT, active INTEGER DEFAULT 1
    )""")
    conn.commit(); conn.close()

def q(sql, args=(), one=False):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, args); r = cur.fetchall()
    conn.commit(); conn.close()
    return (dict(r[0]) if r else None) if one else [dict(x) for x in r]

class H(BaseHTTPRequestHandler):
    def _j(self, d, s=200):
        self.send_response(s)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        self.wfile.write(json.dumps(d, ensure_ascii=False).encode())
    def _b(self):
        n = int(self.headers.get("Content-Length",0))
        return json.loads(self.rfile.read(n)) if n else {}
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","POST,GET,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()
    def do_GET(self):
        if self.path=="/health": self._j({"status":"ok"})
        else: self._j({"error":"Not found"},404)
    def do_POST(self):
        b=self._b(); p=self.path
        if p=="/validate": self._v(b)
        elif p=="/check": self._c(b)
        elif p=="/admin/register": self._r(b)
        elif p=="/admin/list": self._l(b)
        else: self._j({"error":"Not found"},404)
    def _v(self,b):
        c=b.get("code","").strip().upper()
        if not c: return self._j({"valid":False,"message":"请输入赞助码"})
        r=q("SELECT * FROM licenses WHERE code=?",(c,),one=True)
        if not r: return self._j({"valid":False,"message":"赞助码无效"})
        if not r["active"]: return self._j({"valid":False,"message":"已禁用"})
        e=r["expires_at"]
        if e:
            try:
                if datetime.fromisoformat(e)<datetime.now():
                    return self._j({"valid":False,"message":"已过期","expires_at":e})
            except: pass
        if r["max_uses"]>0 and r["uses"]>=r["max_uses"]:
            return self._j({"valid":False,"message":"已达上限"})
        q("UPDATE licenses SET uses=uses+1,last_used=? WHERE code=?",(datetime.now().isoformat(),c))
        self._j({"valid":True,"tier":r["tier"],"expires_at":e,"message":f"有效至{e or"永久"}"})
    def _c(self,b):
        c=b.get("code","").strip().upper()
        r=q("SELECT code,tier,expires_at,active FROM licenses WHERE code=?",(c,),one=True)
        if not r or not r["active"]: return self._j({"valid":False})
        e=r["expires_at"]
        if e:
            try:
                if datetime.fromisoformat(e)<datetime.now():
                    return self._j({"valid":False,"expired":True})
            except: pass
        self._j({"valid":True,"tier":r["tier"],"expires_at":e})
    def _r(self,b):
        if b.get("secret")!=ADMIN_SECRET: return self._j({"error":"未授权"},403)
        c="SPONSOR-"+uuid.uuid4().hex[:8].upper()
        t=b.get("tier","full"); d=int(b.get("days",30)); m=int(b.get("max_uses",0))
        e=(datetime.now()+timedelta(days=d)).isoformat() if d>0 else None
        q("INSERT INTO licenses(code,tier,created_at,expires_at,max_uses) VALUES(?,?,?,?,?)",
          (c,t,datetime.now().isoformat(),e,m))
        self._j({"code":c,"tier":t,"expires_at":e,"max_uses":m})
    def _l(self,b):
        if b.get("secret")!=ADMIN_SECRET: return self._j({"error":"未授权"},403)
        self._j({"codes":q("SELECT * FROM licenses ORDER BY created_at DESC")})
    def log_message(self,f,*a):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {a[0]} {a[1]}")

if __name__=="__main__":
    init_db()
    port=int(os.environ.get("PORT",5000))
    class _S(socketserver.ThreadingMixIn,HTTPServer):
        allow_reuse_address=True
        daemon_threads=True
    _S(("0.0.0.0",port),H).serve_forever()
