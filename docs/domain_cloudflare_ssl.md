# HAMI Domain + Cloudflare CDN + SSL — proxy.hamidesigns.shop

## هدف
- لندینگ پیج و پنل ادمین روی `https://proxy.hamidesigns.shop` با SSL و CDN Cloudflare (پرسرعت، ضد DDoS)
- MTProto پروکسی روی `proxy.hamidesigns.shop:443` مستقیم (gray cloud) — چون Cloudflare free TCP proxy نمی‌کنه

## 1. DNS در Cloudflare

1. برو Cloudflare Dashboard → hamidesigns.shop → DNS
2. اضافه کن:
```
Type: A
Name: proxy
Content: YOUR_FOREIGN_SERVER_IP
Proxy status: DNS only (gray cloud) برای MTProto
TTL: Auto
```
3. برای لندینگ و پنل، دو رکورد جدا با orange cloud:
```
Type: A
Name: proxy-cdn
Content: YOUR_FOREIGN_SERVER_IP
Proxy status: Proxied (orange cloud)

Type: CNAME
Name: proxy
Content: proxy-cdn.hamidesigns.shop
Proxy status: Proxied (orange cloud) — ولی برای MTProto باید gray باشه، پس بهتره:
- proxy.hamidesigns.shop gray (MTProto)
- www.proxy.hamidesigns.shop orange (landing) — یا
- proxy-cdn.hamidesigns.shop orange برای وب
```

**توصیه HAMI Pro:**
- `proxy.hamidesigns.shop` → Gray cloud (Direct) → MTProto :443
- `panel.hamidesigns.shop` → Orange cloud (Proxied) → Dashboard :8081 + Landing :80 via Nginx

یا از Cloudflare Tunnel استفاده کن تا هم وب و هم MTProto از تانل امن عبور کنه.

## 2. Nginx + Let's Encrypt SSL برای پنل و لندینگ

```bash
apt install -y nginx certbot python3-certbot-nginx

cat > /etc/nginx/sites-available/hami-proxy <<'EOF'
server {
    listen 80;
    server_name panel.hamidesigns.shop proxy.hamidesigns.shop;

    location / {
        proxy_pass http://127.0.0.1:8081; # admin panel
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /landing/ {
        alias /opt/hami-proxy/web/;
    }
}

server {
    listen 80;
    server_name landing.hamidesigns.shop;

    root /opt/hami-proxy/web;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

ln -s /etc/nginx/sites-available/hami-proxy /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# SSL
certbot --nginx -d panel.hamidesigns.shop -d landing.hamidesigns.shop --non-interactive --agree-tos -m info@hamidesigns.shop
# Auto renew
systemctl enable certbot.timer
```

## 3. Cloudflare SSL Mode

- Cloudflare → SSL/TLS → Overview → Full (Strict) اگر Let's Encrypt داری
- یا Flexible اگر فقط Cloudflare SSL می‌خوای

## 4. MTProto روی 443 مستقیم

MTProto باید مستقیم به IP وصل بشه، نه از طریق Cloudflare HTTP proxy.

برای همین:
- `proxy.hamidesigns.shop` A record gray cloud → IP مستقیم
- کاربر: `tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=ee...`

اگر می‌خوای هم CDN و هم MTProto روی 443 باشه، از **Cloudflare Spectrum** (پولی) یا **Cloudflare Tunnel** استفاده کن:

### Cloudflare Tunnel (رایگان، پیشنهادی HAMI)

```bash
# نصب cloudflared
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | tee /etc/apt/sources.list.d/cloudflared.list
apt update && apt install cloudflared

# لاگین
cloudflared tunnel login

# ساخت تانل
cloudflared tunnel create hami-proxy-tunnel

# کانفیگ
cat > ~/.cloudflared/config.yml <<EOF
tunnel: hami-proxy-tunnel
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: panel.hamidesigns.shop
    service: http://localhost:8081
  - hostname: proxy.hamidesigns.shop
    service: tcp://localhost:443
  - service: http_status:404
EOF

cloudflared tunnel route dns hami-proxy-tunnel panel.hamidesigns.shop
cloudflared tunnel route dns hami-proxy-tunnel proxy.hamidesigns.shop

# اجرا
cloudflared tunnel run hami-proxy-tunnel
# systemd
cloudflared service install
systemctl enable --now cloudflared
```

الان هم وب و هم MTProto از تانل امن Cloudflare عبور می‌کنه، با SSL و ضد DDoS.

## 5. تست

```bash
curl -v https://panel.hamidesigns.shop
# باید 200 + HAMI Admin Panel

# تست MTProto
python3 hami_proxy/speed_test.py --server proxy.hamidesigns.shop --ports 443
```

## 6. HAMI Branding

- لینک‌ها: `tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=ee...&bot=@HamiSmartSystems`
- هشتگ: `#HAMI #AntiFilter #HighSpeed #proxy.hamidesigns.shop`
