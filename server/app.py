import json, sqlite3, uuid, os, socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta

DB = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "licenses.db"))
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "local_dev_only")

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS licenses (
        code TEXT PRIMARY KEY, tier TEXT DEFAULT "full",
        created_at TEXT, expires_at TEXT,
        max_uses INTEGER DEFAULT 0, uses INTEGER DEFAULT 0,
        last_used TEXT, active INTEGER DEFAULT 1, owner TEXT DEFAULT ""
    )""")
    try: conn.execute("ALTER TABLE licenses ADD COLUMN owner TEXT DEFAULT ''")
    except: pass
    try: conn.execute("ALTER TABLE licenses ADD COLUMN project TEXT DEFAULT ''")
    except: pass
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
        elif self.path=="/":
            all_rows = q("SELECT * FROM licenses ORDER BY created_at DESC")
            total = len(all_rows); act = exd = dis = 0
            for r in all_rows:
                if not r["active"]: dis += 1
                else:
                    e = r.get("expires_at")
                    if e:
                        try:
                            if datetime.fromisoformat(e) < datetime.now(): exd += 1
                            else: act += 1
                        except: act += 1
                    else: act += 1
            html = "<!DOCTYPE html><html><head><meta charset=utf-8>"
            html += "<title>光学模拟器 · 管理后台</title><style>"
            html += "body{font-family:-apple-system,sans-serif;max-width:1100px;margin:40px auto;padding:0 20px;color:#333}"
            html += "h1{font-size:24px;margin-bottom:20px}.c{display:flex;gap:16px;margin:20px 0}"
            html += ".cd{padding:20px;border-radius:12px;background:#f0f2f5;flex:1;text-align:center}"
            html += ".cd .n{font-size:32px;font-weight:700}.cd .l{font-size:13px;color:#666;margin-top:4px}"
            html += "table{width:100%;border-collapse:collapse;margin-top:20px}"
            html += "th,td{padding:12px 10px;text-align:left;border-bottom:1px solid #eee;font-size:13px}"
            html += "th{background:#f0f2f5;color:#555}.ok{color:#090;font-weight:600}.ex{color:#c00;font-weight:600}"
            html += ".dis{color:#999}code{background:#f0f0f0;padding:2px 6px;border-radius:4px;font-size:12px}"
            html += ".btn{padding:2px 8px;margin:1px;border:none;border-radius:3px;cursor:pointer;font-size:11px}"
            html += ".btn-ok{background:#d4edda;color:#155724}.btn-ex{background:#f8d7da;color:#721c24}"
            html += ".btn-df{background:#e2e3e5;color:#383d41}"
            html += "</style></head><body>"
            html += "<h1>✨ 光学模拟器 · 赞助管理</h1>"
            html += '<p style="margin-top:-5px;margin-bottom:18px;color:#888;font-size:13px">本项目：光学波包全实验模拟器 + 混沌摆模拟器 · 统一赞助码管理</p>'
            html += f"<div class=c><div class=cd><div class=n>{total}</div><div class=l>总计</div></div>"
            html += f"<div class=cd><div class=n style=color:#090>{act}</div><div class=l>有效</div></div>"
            html += f"<div class=cd><div class=n style=color:#c00>{exd}</div><div class=l>已过期</div></div>"
            html += f"<div class=cd><div class=n style=color:#999>{dis}</div><div class=l>已禁用</div></div></div>"
            html += "<table><tr><th>赞助码</th><th>归属</th><th>项目</th><th>等级</th><th>创建</th><th>过期</th><th>剩余</th><th>使用</th><th>状态</th><th>操作</th></tr>"
            for r in all_rows:
                nm = r.get("owner","") or "-"; e = r.get("expires_at"); sta = ""; cls = ""
                if not r["active"]: sta = "已禁用"; cls = "dis"
                else:
                    if e:
                        try:
                            if datetime.fromisoformat(e) < datetime.now(): sta = "已过期"; cls = "ex"
                            else: sta = "有效"; cls = "ok"
                        except: sta = "有效"; cls = "ok"
                    else: sta = "永久有效"; cls = "ok"
                rem = "永久"
                if e:
                    try:
                        d_ = (datetime.fromisoformat(e) - datetime.now()).days + 1
                        rem = f"{d_}天" if d_ > 0 else "已过期"
                    except: rem = e[:10]
                ed = e[:10] if e else "-"; cr = r["created_at"][:10]
                u = f"{r['uses']}/{r['max_uses'] or '-'}"
                ac = "启用" if not r["active"] else "禁用"
                bc = "btn-ok" if not r["active"] else "btn-ex"
                prj_disp = {'optical':'光学波包','chaos':'混池摆'}.get(r.get('project',''),'通用')
                html += f"<tr><td><code>{r['code']}</code></td><td>{nm}</td><td>{prj_disp}</td><td>{r['tier']}</td><td>{cr}</td><td>{ed}</td><td class={cls}>{rem}</td><td>{u}</td><td class={cls}>{sta}</td>"
                html += f'<td><button class="btn {bc}" onclick="opActive(\'{r["code"]}\',{0 if r["active"] else 1})">{ac}</button>'
                html += f' <button class="btn btn-df" onclick="opDate(\'{r["code"]}\')">到期</button>'
                html += f' <button class="btn btn-df" onclick="opPerm(\'{r["code"]}\')">永久</button></td></tr>'
            html += "</table>"
            html += '<p style=margin-top:30px;color:#999;font-size:12px>'
            html += 'API: <code>POST /validate</code> 验证 · <code>POST /admin/register</code> 生成码 · <code>POST /admin/extend</code> 延期 · <code>POST /admin/set</code> 设定</p>'
            html += '<div style="margin-top:30px;padding:20px;background:#f0f2f5;border-radius:12px">'
            html += '<h3 style="margin:0 0 12px;font-size:16px">生成新赞助码</h3>'
            html += '<select id=op style="padding:8px;margin:4px;width:160px;border:1px solid #ddd;border-radius:4px"><option value="optical">光学波包全实验模拟器</option><option value="chaos">混池摆模拟器</option><option value="">通用（不限定）</option></select><input id=os placeholder="归属人（如：张三）" style="padding:8px;margin:4px;width:160px;border:1px solid #ddd;border-radius:4px">'
            html += '<input id=ds type=number value=30 style="padding:8px;margin:4px;width:70px;border:1px solid #ddd;border-radius:4px">天'
            html += '<input id=ss type=password placeholder="管理员密码" style="padding:8px;margin:4px;width:180px;border:1px solid #ddd;border-radius:4px">'
            html += '<button onclick="gen()" style="padding:8px 20px;margin:4px;background:#1971c2;color:#fff;border:none;border-radius:4px;cursor:pointer">生成</button>'
            html += '<div id=gr style="margin-top:10px;font-size:14px"></div>'
            html += '<script>'
            html += 'var _s=function(){return document.getElementById("ss").value||prompt("管理员密码:")};'
            html += 'function gen(){'
            html += 'var os=document.getElementById("os").value;'
            html += 'var ds=parseInt(document.getElementById("ds").value)||30;'
            html += 'var ss=document.getElementById("ss").value;'
            html += 'fetch("/admin/register",{method:"POST",body:JSON.stringify({secret:ss,days:ds,owner:os,project:document.getElementById("op").value}),headers:{"Content-Type":"application/json"}})'
            html += '.then(function(r){return r.json()})'
            html += '.then(function(d){'
            html += 'if(d.code){document.getElementById("gr").innerHTML="<span style=color:#090>✔ 成功:</span> <code>"+d.code+"</code>";document.getElementById("os").value=""}'
            html += 'else{document.getElementById("gr").innerHTML="<span style=color:#c00>✖ 失败:</span> "+(d.error||d.message||"未知错误")}})};'
            html += 'function opActive(c,a){var s=_s();'
            html += 'fetch("/admin/set",{method:"POST",body:JSON.stringify({secret:s,code:c,active:a?true:false}),headers:{"Content-Type":"application/json"}})'
            html += '.then(function(r){return r.json()}).then(function(d){if(d.code)location.reload();else alert(d.error||"操作失败")})};'
            html += 'function opDate(c){var s=_s();var d=prompt("输入到期日期 (YYYY-MM-DD):");if(!d)return;'
            html += 'fetch("/admin/set",{method:"POST",body:JSON.stringify({secret:s,code:c,expires_at:d+"T23:59:59"}),headers:{"Content-Type":"application/json"}})'
            html += '.then(function(r){return r.json()}).then(function(x){if(x.code)location.reload();else alert(x.error||"操作失败")})};'
            html += 'function opPerm(c){var s=_s();'
            html += 'fetch("/admin/set",{method:"POST",body:JSON.stringify({secret:s,code:c,expires_at:null}),headers:{"Content-Type":"application/json"}})'
            html += '.then(function(r){return r.json()}).then(function(d){if(d.code)location.reload();else alert(d.error||"操作失败")})};'
            html += '</script></div>'
            html += '</p></body></html>'
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        else: self._j({"error":"Not found"},404)
    def do_POST(self):
        b=self._b(); p=self.path
        if p=="/validate": self._v(b)
        elif p=="/check": self._c(b)
        elif p=="/admin/register": self._r(b)
        elif p=="/admin/list": self._l(b)
        elif p=="/admin/extend": self._e(b)
        elif p=="/admin/set": self._s(b)
        else: self._j({"error":"Not found"},404)
    def _v(self,b):
        c=b.get("code","").strip().upper()
        p=b.get("project","").strip()
        if not c: return self._j({"valid":False,"message":"请输入赞助码"})
        if p:
            r=q("SELECT * FROM licenses WHERE code=? AND (project=? OR project='')",(c,p),one=True)
        else:
            r=q("SELECT * FROM licenses WHERE code=?",(c,),one=True)
        if not r: return self._j({"valid":False,"message":"赞助码无效或不属于此项目"})
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
        self._j({"valid":True,"tier":r["tier"],"expires_at":e,"message":f"有效至{e or'永久'}"})
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
        t=b.get("tier","full"); d=int(b.get("days",30)); m=int(b.get("max_uses",0)); o=b.get("owner",""); pr=b.get("project","")
        e=(datetime.now()+timedelta(days=d)).isoformat() if d>0 else None
        q("INSERT INTO licenses(code,tier,created_at,expires_at,max_uses,owner,project) VALUES(?,?,?,?,?,?,?)",
          (c,t,datetime.now().isoformat(),e,m,o,pr))
        self._j({"code":c,"tier":t,"owner":o,"project":pr,"expires_at":e,"max_uses":m})
    def _l(self,b):
        if b.get("secret")!=ADMIN_SECRET: return self._j({"error":"未授权"},403)
        self._j({"codes":q("SELECT * FROM licenses ORDER BY created_at DESC")})
    def _e(self,b):
        if b.get("secret")!=ADMIN_SECRET: return self._j({"error":"未授权"},403)
        code=b.get("code","").strip().upper()
        days=int(b.get("days",30))
        r=q("SELECT * FROM licenses WHERE code=?",(code,),one=True)
        if not r: return self._j({"error":"赞助码不存在"})
        ne=(datetime.now()+timedelta(days=days)).isoformat()
        q("UPDATE licenses SET expires_at=?,active=1 WHERE code=?",(ne,code))
        self._j({"code":code,"new_expires_at":ne,"message":f"已延期至{ne[:10]}"})
    def _s(self,b):
        if b.get("secret")!=ADMIN_SECRET: return self._j({"error":"未授权"},403)
        code=b.get("code","").strip().upper()
        r=q("SELECT * FROM licenses WHERE code=?",(code,),one=True)
        if not r: return self._j({"error":"赞助码不存在"})
        up=[]; p=[]
        if "active" in b:
            up.append("active=?")
            p.append(1 if b["active"] else 0)
        if "expires_at" in b:
            ea=b["expires_at"]
            if ea is None or ea=="":
                up.append("expires_at=NULL")
            else:
                up.append("expires_at=?")
                p.append(ea)
        if not up: return self._j({"error":"没有要更新的字段"})
        p.append(code)
        q(f"UPDATE licenses SET {','.join(up)} WHERE code=?",p)
        nr=q("SELECT * FROM licenses WHERE code=?",(code,),one=True)
        self._j({"code":code,"active":bool(nr["active"]),"expires_at":nr["expires_at"]})
    def log_message(self,f,*a):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {a[0]} {a[1]}")

if __name__=="__main__":
    init_db()
    class _S(socketserver.ThreadingMixIn,HTTPServer):
        allow_reuse_address=True
        daemon_threads=True
    port=int(os.environ.get("PORT",5000))
    _S(("0.0.0.0",port),H).serve_forever()
