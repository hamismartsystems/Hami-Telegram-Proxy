#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAMI Telegram Proxy Web Dashboard — Pro monitoring
- Shows active connections, traffic, secrets, links
- Simple Flask app, no DB, reads docker logs
"""
from flask import Flask, render_template_string, jsonify
import subprocess
import json
from pathlib import Path
import os

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HAMI Telegram Proxy Dashboard — Pro</title>
<style>
body{background:#0F1115; color:#E6E6E6; font-family: Segoe UI, sans-serif; margin:0; padding:20px;}
.card{background:#1E2025; border:1px solid #2A2E35; border-radius:12px; padding:16px; margin:12px 0;}
.badge{background:#4CAF50; color:white; padding:4px 10px; border-radius:12px; font-size:12px; font-weight:700;}
h1{color:#4A90E2;}
a{color:#4A90E2;}
table{width:100%; border-collapse: collapse;}
th, td{padding:8px; border-bottom:1px solid #2A2E35; text-align:left;}
</style>
</head>
<body>
<h1>🌐 HAMI Telegram Proxy — Dashboard Pro</h1>
<div class="card">
<span class="badge">FREE EDITION Lifetime</span> <b>HAMI SMART SYSTEMS</b> — Anti-Filter + High Speed
</div>
<div class="card">
<h3>📊 Status</h3>
<pre id="status">Loading...</pre>
</div>
<div class="card">
<h3>🔗 Proxies</h3>
<pre id="proxies">Loading...</pre>
</div>
<div class="card">
<h3>📈 Traffic (docker logs)</h3>
<pre id="logs" style="max-height:300px; overflow:auto; background:#15181E; padding:10px; border-radius:8px;">Loading...</pre>
</div>
<script>
async function load(){
  let s = await fetch('/api/status').then(r=>r.json());
  document.getElementById('status').textContent = JSON.stringify(s, null, 2);
  let p = await fetch('/api/proxies').then(r=>r.json());
  document.getElementById('proxies').textContent = JSON.stringify(p, null, 2);
  let l = await fetch('/api/logs').then(r=>r.text());
  document.getElementById('logs').textContent = l;
}
load();
setInterval(load, 5000);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/status")
def status():
    try:
        out = subprocess.check_output(["docker", "ps", "--filter", "name=hami-mtproto", "--format", "{{.Names}} {{.Status}}"], text=True)
    except Exception as e:
        out = f"Error: {e}"
    return jsonify({"docker": out, "version": "1.0 HAMI Pro"})

@app.route("/api/proxies")
def proxies():
    p = Path("/opt/hami-proxy/hami_proxies.json")
    if p.exists():
        return jsonify(json.loads(p.read_text()))
    return jsonify({"msg": "No proxies yet, run manager.py"})

@app.route("/api/logs")
def logs():
    try:
        out = subprocess.check_output(["docker", "logs", "--tail", "100", "hami-mtproto"], text=True, stderr=subprocess.STDOUT)
        return out
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
