#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAMI Iran Tunnel — Separate from SSH & Config tunnels
- Provides Iran edge relay for high-speed domestic connection
- Users connect to Iran IP (fast inside Iran), tunnel forwards to foreign MTProto proxy
- Uses FRP (Fast Reverse Proxy) or WireGuard, dedicated port/token

Architecture:
[User IR] -> [Iran Edge :8443] -> [FRP Tunnel AES-256 :7000] -> [Foreign MTProto :443] -> Telegram

Separate: token, ports, binary, systemd service
"""
import os
import sys
import json
from pathlib import Path

CONFIG_TEMPLATE_IRAN = """
# HAMI Iran Tunnel — FRP Client — Separate
[common]
server_addr = {foreign_ip}
server_port = 7000
token = {token}
tls_enable = true
pool_count = 5

[hami-mtproto-iran]
type = tcp
local_ip = 127.0.0.1
local_port = 443
remote_port = {remote_port}
use_encryption = true
use_compression = true
"""

CONFIG_TEMPLATE_FOREIGN = """
# HAMI Iran Tunnel — FRP Server — Separate
[common]
bind_port = 7000
token = {token}
vhost_http_port = 8080
dashboard_port = 7500
dashboard_user = hami
dashboard_pwd = {dashboard_pwd}
log_file = /var/log/frps.log
"""

WIREGUARD_TEMPLATE = """
# HAMI Iran Tunnel — WireGuard — Separate high-speed tunnel
[Interface]
PrivateKey = {private_key}
Address = 10.200.200.1/24
ListenPort = 51821
SaveConfig = true
# BBR, fast

[Peer]
PublicKey = {peer_public}
AllowedIPs = 10.200.200.2/32
"""

def generate_frp_configs(foreign_ip, iran_ip, token=None, remote_port=8443):
    import secrets
    if not token:
        token = secrets.token_urlsafe(16)
    dashboard_pwd = secrets.token_urlsafe(12)

    iran_cfg = CONFIG_TEMPLATE_IRAN.format(
        foreign_ip=foreign_ip,
        token=token,
        remote_port=remote_port
    )
    foreign_cfg = CONFIG_TEMPLATE_FOREIGN.format(
        token=token,
        dashboard_pwd=dashboard_pwd
    )

    return {
        "iran_frp": iran_cfg,
        "foreign_frp": foreign_cfg,
        "token": token,
        "dashboard_pwd": dashboard_pwd,
        "remote_port": remote_port,
        "iran_ip": iran_ip,
        "foreign_ip": foreign_ip,
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="HAMI Iran Tunnel Generator — Separate")
    parser.add_argument("--foreign-ip", required=True, help="Foreign server IP (MTProto)")
    parser.add_argument("--iran-ip", required=True, help="Iran edge server IP")
    parser.add_argument("--remote-port", type=int, default=8443, help="Remote port on foreign for Iran relay")
    parser.add_argument("--out", default="./iran_tunnel_configs", help="Output dir")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    cfgs = generate_frp_configs(args.foreign_ip, args.iran_ip, remote_port=args.remote_port)

    (out / "frpc_iran.ini").write_text(cfgs["iran_frp"], encoding="utf-8")
    (out / "frps_foreign.ini").write_text(cfgs["foreign_frp"], encoding="utf-8")

    info = {
        "foreign_ip": cfgs["foreign_ip"],
        "iran_ip": cfgs["iran_ip"],
        "token": cfgs["token"],
        "remote_port": cfgs["remote_port"],
        "dashboard_pwd": cfgs["dashboard_pwd"],
        "user_connect": f"{cfgs['iran_ip']}:{cfgs['remote_port']} -> {cfgs['foreign_ip']}:443 -> Telegram",
        "tg_link_iran": f"tg://proxy?server={cfgs['iran_ip']}&port={cfgs['remote_port']}&secret=ee... (use same secret as foreign)",
    }
    (out / "tunnel_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")

    print("✅ HAMI Iran Tunnel configs generated (Separate from SSH/Config)")
    print(f"Foreign: {cfgs['foreign_ip']}:7000 (FRP server)")
    print(f"Iran: {cfgs['iran_ip']} -> {cfgs['foreign_ip']}:{cfgs['remote_port']}")
    print(f"Token: {cfgs['token']}")
    print(f"User connects to: {cfgs['iran_ip']}:{cfgs['remote_port']} (fast inside Iran)")
    print(f"Files in {out}")

if __name__ == "__main__":
    main()
