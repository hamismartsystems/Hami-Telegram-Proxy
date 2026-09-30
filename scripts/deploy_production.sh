#!/bin/bash
# HAMI Telegram Proxy — Production Deploy — proxy.hamidesigns.shop
# One-click full deploy: MTProto + Domain + SSL + Cloudflare DNS + Panel+Bot + Iran Tunnel
# Developed by HAMI SMART SYSTEMS — Pro Max
# Usage: sudo ./deploy_production.sh --foreign-ip YOUR_IP --iran-ip IRAN_IP --cf-token CF_API_TOKEN --bot-token BOT_TOKEN
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

FOREIGN_IP=""
IRAN_IP=""
CF_TOKEN=""
BOT_TOKEN=""
DOMAIN="hamidesigns.shop"
SUB_PROXY="proxy"
SUB_PANEL="panel"
SUB_LANDING="landing"

while [[ $# -gt 0 ]]; do
  case $1 in
    --foreign-ip) FOREIGN_IP="$2"; shift 2;;
    --iran-ip) IRAN_IP="$2"; shift 2;;
    --cf-token) CF_TOKEN="$2"; shift 2;;
    --bot-token) BOT_TOKEN="$2"; shift 2;;
    *) shift;;
  esac
done

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Run with sudo${NC}"
  exit 1
fi

if [ -z "$FOREIGN_IP" ]; then
  FOREIGN_IP=$(curl -s https://api.ipify.org || hostname -I | awk '{print $1}')
fi

echo -e "${BLUE}██╗  ██╗ █████╗ ███╗   ███╗██╗   ████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ██╗  ██╗"
echo "██║  ██║██╔══██╗████╗ ████║██║   ╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗╚██╗██╔╝"
echo "██║  ██║███████║██╔████╔██║██║      ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║ ╚███╔╝ "
echo "██║  ██║██╔══██║██║╚██╔╝██║██║      ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔═══╝ ██╔══██║ ██╔██╗ "
echo "╚█████╔╝██║  ██║██║ ╚═╝ ██║██║      ██║   ███████╗███████╗███████╗╚██████╔╝██║     ██║  ██║██╔╝ ██╗"
echo -e "${NC}"
echo -e "${YELLOW}HAMI Telegram Proxy — Production Deploy — v1.4 Pro Max${NC}"
echo -e "Foreign IP: $FOREIGN_IP | Iran IP: $IRAN_IP | Domain: $DOMAIN"

echo -e "${BLUE}[1/8] پیش‌نیازها...${NC}"
apt update -y
apt install -y docker.io curl openssl python3 python3-pip nginx certbot python3-certbot-nginx qrencode jq

echo -e "${BLUE}[2/8] BBR + بهینه‌سازی سرعت...${NC}"
if ! grep -q "net.core.default_qdisc=fq" /etc/sysctl.conf; then
  cat >> /etc/sysctl.conf <<EOF
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
net.ipv4.tcp_fastopen=3
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
EOF
  sysctl -p
fi
ulimit -n 65535
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

echo -e "${BLUE}[3/8] Cloudflare DNS اتوماتیک (اگه توکن دادی)...${NC}"
if [ -n "$CF_TOKEN" ]; then
  # Get zone ID
  ZONE_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN" -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" | jq -r '.result[0].id')
  echo "Zone ID: $ZONE_ID"
  if [ "$ZONE_ID" != "null" ] && [ -n "$ZONE_ID" ]; then
    for SUB in $SUB_PROXY $SUB_PANEL $SUB_LANDING; do
      # Check if record exists
      REC_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records?name=$SUB.$DOMAIN" -H "Authorization: Bearer $CF_TOKEN" | jq -r '.result[0].id')
      if [ "$REC_ID" == "null" ] || [ -z "$REC_ID" ]; then
        echo "Creating DNS $SUB.$DOMAIN -> $FOREIGN_IP"
        curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
          -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
          --data "{\"type\":\"A\",\"name\":\"$SUB\",\"content\":\"$FOREIGN_IP\",\"ttl\":120,\"proxied\":false}" | jq .
      else
        echo "Updating DNS $SUB.$DOMAIN -> $FOREIGN_IP"
        curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$REC_ID" \
          -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
          --data "{\"type\":\"A\",\"name\":\"$SUB\",\"content\":\"$FOREIGN_IP\",\"ttl\":120,\"proxied\":false}" | jq .
      fi
    done
    echo -e "${GREEN}DNS Cloudflare ست شد — حالا proxy gray, panel/landing می‌تونی orange کنی از داشبورد Cloudflare${NC}"
  else
    echo -e "${RED}Zone ID پیدا نشد — DNS دستی ست کن${NC}"
  fi
else
  echo -e "${YELLOW}CF_TOKEN ندادی — DNS دستی باید ست کنی:${NC}"
  echo "  proxy.$DOMAIN A $FOREIGN_IP gray"
  echo "  panel.$DOMAIN A $FOREIGN_IP orange"
  echo "  landing.$DOMAIN A $FOREIGN_IP orange"
fi

echo -e "${BLUE}[4/8] MTProto Proxy نصب (3 سکرت Fake-TLS)...${NC}"
mkdir -p /opt/hami-proxy/web
cd /opt/hami-proxy

SECRET1=$(head /dev/urandom | tr -dc A-F0-9 | head -c32)
SECRET2=$(head /dev/urandom | tr -dc A-F0-9 | head -c32)
SECRET3=$(head /dev/urandom | tr -dc A-F0-9 | head -c32)

docker pull telegrammessenger/mtg:latest >/dev/null 2>&1 || true
FAKE1=$(docker run --rm telegrammessenger/mtg generate-secret -c google.com $SECRET1 2>/dev/null || echo "ee$SECRET1")
FAKE2=$(docker run --rm telegrammessenger/mtg generate-secret -c cloudflare.com $SECRET2 2>/dev/null || echo "ee$SECRET2")
FAKE3=$(docker run --rm telegrammessenger/mtg generate-secret -c www.microsoft.com $SECRET3 2>/dev/null || echo "ee$SECRET3")

cat > /opt/hami-proxy/secrets.txt <<EOF
# HAMI Telegram Proxy — Production — $(date)
# Foreign: $FOREIGN_IP — Domain: proxy.$DOMAIN

SECRET_GOOGLE=$FAKE1
SECRET_CLOUDFLARE=$FAKE2
SECRET_MICROSOFT=$FAKE3

LINKS:
tg://proxy?server=$FOREIGN_IP&port=443&secret=$FAKE1&bot=@HamiSmartSystems
tg://proxy?server=$FOREIGN_IP&port=443&secret=$FAKE2&bot=@HamiSmartSystems
tg://proxy?server=$FOREIGN_IP&port=443&secret=$FAKE3&bot=@HamiSmartSystems

DOMAIN LINKS:
tg://proxy?server=proxy.$DOMAIN&port=443&secret=$FAKE1&bot=@HamiSmartSystems
tg://proxy?server=proxy.$DOMAIN&port=443&secret=$FAKE2&bot=@HamiSmartSystems

IRAN TUNNEL (if Iran IP $IRAN_IP):
tg://proxy?server=$IRAN_IP&port=8443&secret=$FAKE1&bot=@HamiSmartSystems
EOF

docker rm -f hami-mtproto hami-mtproto-2 hami-mtproto-3 2>/dev/null || true
docker run -d --name hami-mtproto --restart=always -p 443:443 telegrammessenger/mtg:latest run --cloak-port 993 -b 0.0.0.0:443 -4 $FOREIGN_IP:443 $FAKE1 --allow-replay
docker run -d --name hami-mtproto-2 --restart=always -p 8443:443 telegrammessenger/mtg:latest run -b 0.0.0.0:443 $FAKE2 || true
docker run -d --name hami-mtproto-3 --restart=always -p 8444:443 telegrammessenger/mtg:latest run -b 0.0.0.0:443 $FAKE3 || true

echo -e "${BLUE}[5/8] Nginx + SSL Let's Encrypt...${NC}"
# Copy web
cp -r /root/hami-telegram-proxy/web/* /opt/hami-proxy/web/ 2>/dev/null || echo "Web dir not found, creating placeholder"
cat > /opt/hami-proxy/web/index.html <<'HTML'
<!doctype html><html><head><meta charset="utf-8"><title>HAMI Proxy</title></head><body><h1>HAMI Telegram Proxy Pro — Ready</h1><p>See /opt/hami-proxy/secrets.txt</p></body></html>
HTML

cat > /etc/nginx/sites-available/hami-proxy <<EOF
server {
    listen 80;
    server_name panel.$DOMAIN landing.$DOMAIN;
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
ln -sf /etc/nginx/sites-available/hami-proxy /etc/nginx/sites-enabled/hami-proxy
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# SSL
certbot --nginx -d panel.$DOMAIN -d landing.$DOMAIN --non-interactive --agree-tos -m info@hamidesigns.shop || echo "Certbot failed — check DNS propagation, try later"

echo -e "${BLUE}[6/8] پنل ادمین + ربات ترکیبی...${NC}"
cd /root/hami-telegram-proxy 2>/dev/null || cd /opt/hami-proxy
pip3 install flask python-telegram-bot qrcode[pil] --break-system-packages 2>/dev/null || pip3 install flask python-telegram-bot qrcode

cat > /etc/systemd/system/hami-combined.service <<EOF
[Unit]
Description=HAMI Combined Panel+Bot+Dashboard Pro Max
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/hami-proxy
Environment=HAMI_BOT_TOKEN=$BOT_TOKEN
Environment=HAMI_ADMIN_USER=admin
Environment=HAMI_ADMIN_PASS=Hami@2026Pro
ExecStart=/usr/bin/python3 /root/hami-telegram-proxy/hami_proxy/combined_panel_bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now hami-combined || true

echo -e "${BLUE}[7/8] تانل ایران جدا (اگه IP ایران دادی)...${NC}"
if [ -n "$IRAN_IP" ]; then
  mkdir -p /opt/hami-proxy/iran_tunnel
  cat > /opt/hami-proxy/iran_tunnel/frps_foreign.ini <<EOF
[common]
bind_port = 7000
token = HAMI_SECURE_$(openssl rand -hex 8)
dashboard_port = 7500
dashboard_user = hami
dashboard_pwd = $(openssl rand -hex 6)
EOF
  echo "FRP server config in /opt/hami-proxy/iran_tunnel/frps_foreign.ini"
  echo "On Iran server run:"
  echo "  frpc -c frpc_iran.ini (see docs/iran_tunnel.md)"
fi

echo -e "${BLUE}[8/8] QR + نهایی...${NC}"
qrencode -o /opt/hami-proxy/qr_google.png "tg://proxy?server=proxy.$DOMAIN&port=443&secret=$FAKE1" 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ دیپلوی کامل HAMI Telegram Proxy Pro Max انجام شد!${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════${NC}"
cat /opt/hami-proxy/secrets.txt
echo -e "${YELLOW}════════════════════════════════════════════════${NC}"
echo -e "🌐 Landing: https://landing.$DOMAIN (or http://$FOREIGN_IP:8080)"
echo -e "🔐 Admin Panel: https://panel.$DOMAIN (admin / Hami@2026Pro)"
echo -e "📊 Dashboard: http://$FOREIGN_IP:8080"
echo -e "🤖 Bot: set BOT_TOKEN and systemctl status hami-combined"
echo -e "📦 Logs: docker logs -f hami-mtproto"
echo -e "🇮🇷 Iran Tunnel: see /opt/hami-proxy/iran_tunnel/"
echo -e "${YELLOW}Developed by HAMI SMART SYSTEMS — Pro Max — دعای کاربران بدرقه راه ❤️${NC}"
