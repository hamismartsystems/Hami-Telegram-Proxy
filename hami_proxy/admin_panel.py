#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAMI Admin Panel — Pro Web UI for Telegram Proxy Management
- Login, stats, secret management, user banning, link generation, channel auto-post
- Branded HAMI SMART SYSTEMS — dark theme like HDM
"""
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import json
import os
import secrets
from pathlib import Path
from datetime import datetime
import subprocess

app = Flask(__name__)
app.secret_key = "HAMI_SMART_SYSTEMS_PRO_2026_SECRET_KEY"

ADMIN_USER = os.getenv("HAMI_ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("HAMI_ADMIN_PASS", "Hami@2026")

PROXY_FILE = Path("/opt/hami-proxy/hami_proxies.json")
STATS_FILE = Path("/opt/hami-proxy/stats.json")

HTML_LOGIN = """
<!doctype html>
<html><head><meta charset="utf-8"><title>HAMI Admin Login</title>
<style>
body{background:#0F1115; color:#E6E6E6; font-family: Segoe UI; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;}
.card{background:#1E2025; border:1px solid #2A2E35; border-radius:16px; padding:32px; width:380px;}
input{background:#2A2E35; border:1px solid #3A4050; border-radius:8px; padding:10px; color:#E6E6E6; width:100%; margin:8px 0;}
button{background:#4A90E2; border:0; border-radius:8px; padding:10px; color:white; width:100%; font-weight:700; cursor:pointer;}
button:hover{background:#5AA0F2;}
</style></head>
<body>
<div class="card">
<h2>🌐 HAMI Admin — Login</h2>
<p style="color:#8B90A0; font-size:12px;">HAMI SMART SYSTEMS — Telegram Proxy Pro</p>
<form method="post">
<input name="user" placeholder="Username" required>
<input name="pass" type="password" placeholder="Password" required>
<button type="submit">Login</button>
</form>
</div>
</body></html>
"""

HTML_ADMIN = """
<!doctype html>
<html><head><meta charset="utf-8"><title>HAMI Admin Panel Pro</title>
<style>
body{background:#0F1115; color:#E6E6E6; font-family: Segoe UI; margin:0;}
header{background:#1E2025; border-bottom:1px solid #2A2E35; padding:12px 20px; display:flex; justify-content:space-between; align-items:center;}
.card{background:#1E2025; border:1px solid #2A2E35; border-radius:12px; padding:16px; margin:16px;}
.badge{background:#4CAF50; color:white; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700;}
table{width:100%; border-collapse:collapse;}
th,td{padding:10px; border-bottom:1px solid #2A2E35; text-align:left; font-size:13px;}
button{background:#2A2E35; border:1px solid #3A4050; border-radius:8px; padding:6px 12px; color:#E6E6E6; cursor:pointer;}
button.primary{background:#4A90E2; border:0; color:white; font-weight:600;}
button:hover{border-color:#4A90E2;}
input,select{background:#2A2E35; border:1px solid #3A4050; border-radius:8px; padding:8px; color:#E6E6E6;}
.grid{display:grid; grid-template-columns: 1fr 1fr; gap:16px;}
@media(max-width:800px){.grid{grid-template-columns:1fr;}}
</style>
</head>
<body>
<header>
<div><b>🌐 HAMI Telegram Proxy</b> <span class="badge">PRO v1.2</span> — Admin Panel</div>
<div><a href="/logout" style="color:#8B90A0; text-decoration:none;">Logout</a></div>
</header>

<div class="grid">
<div class="card">
<h3>📊 Stats</h3>
<pre id="stats">Loading...</pre>
<button onclick="loadStats()">Refresh</button>
</div>

<div class="card">
<h3>➕ Generate New Proxy</h3>
<label>Fake Domain:</label>
<select id="domain">
<option>google.com</option>
<option>cloudflare.com</option>
<option>www.microsoft.com</option>
<option>www.amazon.com</option>
<option>azure.microsoft.com</option>
</select><br><br>
<button class="primary" onclick="genProxy()">Generate</button>
<pre id="genResult"></pre>
</div>
</div>

<div class="card">
<h3>🔗 Proxies</h3>
<table><thead><tr><th>ID</th><th>Domain</th><th>Secret</th><th>TG Link</th><th>Action</th></tr></thead><tbody id="proxyTable"></tbody></table>
</div>

<div class="card">
<h3>📢 Auto Post to Channel</h3>
<p style="color:#8B90A0; font-size:12px;">ارسال خودکار لیست پروکسی‌ها به کانال تلگرام HAMI</p>
<input id="channel" placeholder="@HamiProxyChannel" style="width:200px;">
<button class="primary" onclick="postChannel()">Post</button>
<pre id="postResult"></pre>
</div>

<script>
async function loadStats(){
  let s = await fetch('/api/stats').then(r=>r.json());
  document.getElementById('stats').textContent = JSON.stringify(s, null, 2);
  let proxies = await fetch('/api/proxies').then(r=>r.json());
  let tbody = document.getElementById('proxyTable');
  tbody.innerHTML = '';
  proxies.forEach(p=>{
    let tr = document.createElement('tr');
    tr.innerHTML = `<td>${p.id}</td><td>${p.domain}</td><td style="font-size:10px;">${p.fake_secret.substring(0,16)}...</td><td><a href="${p.tg_link}" style="color:#4A90E2;">Connect</a></td><td><button onclick="copyLink('${p.tg_link}')">Copy</button> <button onclick="banProxy('${p.fake_secret}')">Ban</button></td>`;
    tbody.appendChild(tr);
  });
}
async function genProxy(){
  let domain = document.getElementById('domain').value;
  let res = await fetch('/api/generate', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({domain})}).then(r=>r.json());
  document.getElementById('genResult').textContent = JSON.stringify(res, null, 2);
  loadStats();
}
function copyLink(link){ navigator.clipboard.writeText(link); alert('Copied: '+link); }
async function banProxy(secret){ if(confirm('Ban '+secret.substring(0,10)+'...?')){ await fetch('/api/ban', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({secret})}); loadStats(); } }
async function postChannel(){
  let ch = document.getElementById('channel').value;
  let res = await fetch('/api/post_channel', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({channel:ch})}).then(r=>r.json());
  document.getElementById('postResult').textContent = JSON.stringify(res, null, 2);
}
loadStats();
setInterval(loadStats, 5000);
</script>
</body>
</html>
"""

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form.get("user")==ADMIN_USER and request.form.get("pass")==ADMIN_PASS:
            session["admin"]=True
            return redirect(url_for("admin"))
        return "❌ Wrong credentials", 403
    return render_template_string(HTML_LOGIN)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))
    return render_template_string(HTML_ADMIN)

@app.route("/api/stats")
def api_stats():
    if not session.get("admin"):
        return jsonify({"error":"unauthorized"}), 401
    if STATS_FILE.exists():
        return jsonify(json.loads(STATS_FILE.read_text()))
    return jsonify({"uptime":0, "total_connections":0})

@app.route("/api/proxies")
def api_proxies():
    if not session.get("admin"):
        return jsonify({"error":"unauthorized"}), 401
    if PROXY_FILE.exists():
        return jsonify(json.loads(PROXY_FILE.read_text()))
    return jsonify([])

@app.route("/api/generate", methods=["POST"])
def api_generate():
    if not session.get("admin"):
        return jsonify({"error":"unauthorized"}), 401
    data = request.json or {}
    domain = data.get("domain","google.com")
    # generate
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from manager import gen_fake_tls_secret, gen_tg_link, gen_https_link
    fake_secret, dom, raw = gen_fake_tls_secret(domain)
    # append to file
    proxies = []
    if PROXY_FILE.exists():
        proxies = json.loads(PROXY_FILE.read_text())
    new_id = max([p["id"] for p in proxies], default=0)+1
    new_proxy = {
        "id": new_id,
        "domain": domain,
        "raw_secret": raw,
        "fake_secret": fake_secret,
        "tg_link": gen_tg_link("YOUR_SERVER_IP", 443, fake_secret, bot="@HamiSmartSystems"),
        "https_link": gen_https_link("YOUR_SERVER_IP", 443, fake_secret),
    }
    proxies.append(new_proxy)
    PROXY_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROXY_FILE.write_text(json.dumps(proxies, indent=2, ensure_ascii=False), encoding="utf-8")
    return jsonify(new_proxy)

@app.route("/api/ban", methods=["POST"])
def api_ban():
    if not session.get("admin"):
        return jsonify({"error":"unauthorized"}), 401
    # In real impl, add to banned list and restart mtg with new secret
    return jsonify({"status":"banned (demo)"})

@app.route("/api/post_channel", methods=["POST"])
def api_post_channel():
    if not session.get("admin"):
        return jsonify({"error":"unauthorized"}), 401
    # Demo: would use bot to post to channel
    return jsonify({"status":"posted to channel (demo) — integrate bot token"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8081, debug=False)
