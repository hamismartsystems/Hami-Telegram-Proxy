#!/bin/bash
# HAMI Domain + SSL + Cloudflare Setup — proxy.hamidesigns.shop
# One-click setup for Nginx + Let's Encrypt + Cloudflare Tunnel (optional)
set -e

DOMAIN_PANEL="panel.hamidesigns.shop"
DOMAIN_LANDING="landing.hamidesigns.shop"
DOMAIN_PROXY="proxy.hamidesigns.shop"
EMAIL="info@hamidesigns.shop"

if [ "$EUID" -ne 0 ]; then
  echo "Run with sudo: sudo ./setup_domain_ssl.sh"
  exit 1
fi

echo "🌐 HAMI Domain + SSL Setup — $DOMAIN_PANEL + $DOMAIN_LANDING + $DOMAIN_PROXY"

apt update -y
apt install -y nginx certbot python3-certbot-nginx curl

# Copy nginx config
mkdir -p /opt/hami-proxy/web
cp -r ../web/* /opt/hami-proxy/web/ 2>/dev/null || true
cp ../nginx/hami-proxy.conf /etc/nginx/sites-available/hami-proxy 2>/dev/null || cat > /etc/nginx/sites-available/hami-proxy <<'EOF'
server {
    listen 80;
    server_name panel.hamidesigns.shop landing.hamidesigns.shop;
    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/hami-proxy /etc/nginx/sites-enabled/hami-proxy
nginx -t && systemctl reload nginx

echo "🔐 Getting Let's Encrypt SSL for $DOMAIN_PANEL and $DOMAIN_LANDING..."
certbot --nginx -d $DOMAIN_PANEL -d $DOMAIN_LANDING --non-interactive --agree-tos -m $EMAIL || echo "Certbot failed, check DNS"

echo "✅ SSL setup done"
echo "Now set Cloudflare DNS:"
echo " - $DOMAIN_PROXY A YOUR_IP gray cloud (Direct) for MTProto :443"
echo " - $DOMAIN_PANEL A YOUR_IP orange cloud (Proxied) for Admin"
echo " - $DOMAIN_LANDING A YOUR_IP orange cloud for Landing"

echo ""
echo "Optional: Cloudflare Tunnel for both web + MTProto via CDN:"
echo "  curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null"
echo "  echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | tee /etc/apt/sources.list.d/cloudflared.list"
echo "  apt update && apt install cloudflared"
echo "  cloudflared tunnel login"
echo "  cloudflared tunnel create hami-proxy-tunnel"
echo "  # See docs/domain_cloudflare_ssl.md for full config"

echo ""
echo "🌐 HAMI Domains ready — https://$DOMAIN_PANEL and https://$DOMAIN_LANDING"
echo "🔗 MTProto: tg://proxy?server=$DOMAIN_PROXY&port=443&secret=ee..."
