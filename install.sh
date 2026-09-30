#!/bin/bash
# HAMI Telegram Proxy — One-click installer — Anti-Filter + High Speed + Iran Tunnel Separate
# Developed by HAMI SMART SYSTEMS — Pro & Nab
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "██╗  ██╗ █████╗ ███╗   ███╗██╗   ████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗"
echo "██║  ██║██╔══██╗████╗ ████║██║   ╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║"
echo "███████║███████║██╔████╔██║██║      ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║"
echo "██╔══██║██╔══██║██║╚██╔╝██║██║      ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║"
echo "██║  ██║██║  ██║██║ ╚═╝ ██║██║      ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║"
echo "╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝      ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝"
echo -e "${NC}"
echo -e "${YELLOW}HAMI SMART SYSTEMS — Telegram MTProto Anti-Filter Pro — v1.0${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}لطفاً با sudo اجرا کنید: sudo ./install.sh${NC}"
  exit 1
fi

SERVER_IP=$(curl -s https://api.ipify.org || hostname -I | awk '{print $1}')
echo -e "${GREEN}سرور IP: $SERVER_IP${NC}"

echo -e "${BLUE}[1/6] نصب پیش‌نیازها...${NC}"
apt update -y
apt install -y docker.io curl openssl python3 python3-pip qrencode

echo -e "${BLUE}[2/6] فعال‌سازی BBR برای سرعت بالا...${NC}"
if ! grep -q "net.core.default_qdisc=fq" /etc/sysctl.conf; then
  echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
  echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
  sysctl -p
  echo -e "${GREEN}BBR فعال شد${NC}"
fi

echo -e "${BLUE}[3/6] ساخت پوشه HAMI...${NC}"
mkdir -p /opt/hami-proxy
cd /opt/hami-proxy

echo -e "${BLUE}[4/6] تولید 3 سکرت Fake-TLS حرفه‌ای...${NC}"
# تولید سکرت‌های معمولی
SECRET1=$(head /dev/urandom | tr -dc A-F0-9 | head -c32)
SECRET2=$(head /dev/urandom | tr -dc A-F0-9 | head -c32)
SECRET3=$(head /dev/urandom | tr -dc A-F0-9 | head -c32)

# تبدیل به Fake-TLS با دامنه‌های محبوب
docker pull telegrammessenger/mtg:latest >/dev/null 2>&1 || true

FAKE1=$(docker run --rm telegrammessenger/mtg generate-secret -c google.com $SECRET1 2>/dev/null || echo "ee${SECRET1}google.com" | xxd -p | tr -d '\n' | head -c 64)
FAKE2=$(docker run --rm telegrammessenger/mtg generate-secret -c cloudflare.com $SECRET2 2>/dev/null || echo "ee${SECRET2}cloudflare.com" | xxd -p | tr -d '\n' | head -c 64)
FAKE3=$(docker run --rm telegrammessenger/mtg generate-secret -c www.microsoft.com $SECRET3 2>/dev/null || echo "ee${SECRET3}microsoft.com" | xxd -p | tr -d '\n' | head -c 64)

# اگر docker generate-secret کار نکرد، ee + secret ساده
if [[ ! $FAKE1 == ee* ]]; then FAKE1="ee${SECRET1}"; fi
if [[ ! $FAKE2 == ee* ]]; then FAKE2="ee${SECRET2}"; fi
if [[ ! $FAKE3 == ee* ]]; then FAKE3="ee${SECRET3}"; fi

echo "SECRET1: $FAKE1 (google.com)"
echo "SECRET2: $FAKE2 (cloudflare.com)"
echo "SECRET3: $FAKE3 (microsoft.com)"

cat > /opt/hami-proxy/secrets.txt <<EOF
# HAMI Telegram Proxy Secrets — $(date)
# Server: $SERVER_IP:443
# Fake-TLS domains: google.com, cloudflare.com, www.microsoft.com

SECRET_GOOGLE=$FAKE1
SECRET_CLOUDFLARE=$FAKE2
SECRET_MICROSOFT=$FAKE3

# Links:
# Google:
tg://proxy?server=$SERVER_IP&port=443&secret=$FAKE1
# Cloudflare:
tg://proxy?server=$SERVER_IP&port=443&secret=$FAKE2
# Microsoft:
tg://proxy?server=$SERVER_IP&port=443&secret=$FAKE3

# HAMI Branded:
tg://proxy?server=$SERVER_IP&port=443&secret=$FAKE1&bot=@HamiSmartSystems
EOF

echo -e "${BLUE}[5/6] راه‌اندازی MTProto Proxy (mtg)...${NC}"
# استفاده از اولین سکرت برای mtg اصلی، بقیه برای چند نمونه
docker rm -f hami-mtproto 2>/dev/null || true
docker run -d --name hami-mtproto --restart=always -p 443:443 \
  telegrammessenger/mtg:latest run --cloak-port 993 \
  -b 0.0.0.0:443 -4 ${SERVER_IP}:443 ${FAKE1} --allow-replay --prefer-ip="prefer-ipv4" || \
docker run -d --name hami-mtproto --restart=always -p 443:443 \
  9seconds/mtg:latest run --cloak-port 993 \
  -b 0.0.0.0:443 ${FAKE1}

# نمونه دوم و سوم روی پورت‌های دیگر برای تنوع
docker rm -f hami-mtproto-2 hami-mtproto-3 2>/dev/null || true
docker run -d --name hami-mtproto-2 --restart=always -p 8443:443 \
  telegrammessenger/mtg:latest run -b 0.0.0.0:443 ${FAKE2} || true
docker run -d --name hami-mtproto-3 --restart=always -p 8444:443 \
  telegrammessenger/mtg:latest run -b 0.0.0.0:443 ${FAKE3} || true

echo -e "${BLUE}[6/6] ساخت سرویس systemd و QR...${NC}"
cat > /etc/systemd/system/hami-mtproto.service <<EOF
[Unit]
Description=HAMI Telegram MTProto Proxy Pro
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a hami-mtproto
ExecStop=/usr/bin/docker stop hami-mtproto

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable hami-mtproto

# QR کد
if command -v qrencode &> /dev/null; then
  qrencode -o /opt/hami-proxy/qr_google.png "tg://proxy?server=$SERVER_IP&port=443&secret=$FAKE1" || true
  qrencode -o /opt/hami-proxy/qr_cloudflare.png "tg://proxy?server=$SERVER_IP&port=443&secret=$FAKE2" || true
fi

echo ""
echo -e "${GREEN}✅ نصب کامل شد — HAMI Telegram Proxy Pro${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════${NC}"
cat /opt/hami-proxy/secrets.txt
echo -e "${YELLOW}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}QR کدها در /opt/hami-proxy/qr_*.png${NC}"
echo -e "${BLUE}لاگ: docker logs -f hami-mtproto${NC}"
echo -e "${BLUE}پنل مانیتورینگ: python3 hami_proxy/web_dashboard.py${NC}"
echo ""
echo -e "${GREEN}برای تانل ایران جدا، فایل docs/iran_tunnel.md را ببینید${NC}"
echo -e "${YELLOW}Developed by HAMI SMART SYSTEMS — دعای کاربران بدرقه راه ❤️${NC}"
