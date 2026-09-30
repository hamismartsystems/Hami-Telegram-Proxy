# HAMI Telegram Proxy — Deploy on Finland Server 65.109.186.210 — Production

## DNS Already Done ✅
```
proxy.hamidesigns.shop A 65.109.186.210 (gray cloud - Direct for MTProto)
panel.hamidesigns.shop A 65.109.186.210 (gray, will be orange after SSL)
landing.hamidesigns.shop A 65.109.186.210
mtproto.hamidesigns.shop A 65.109.186.210
```

## Secrets Generated ✅ (proxy.hamidesigns.shop)
```
1. www.microsoft.com: eeYOUR_SECRET_HERE_1
   tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=eeYOUR_SECRET_HERE_1&bot=@HamiSmartSystems

2. www.microsoft.com: eeYOUR_SECRET_HERE_2
   tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=eeYOUR_SECRET_HERE_2&bot=@HamiSmartSystems

3. google.com: eeYOUR_SECRET_HERE_3
   tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=eeYOUR_SECRET_HERE_3&bot=@HamiSmartSystems
```

## Steps on Finland Server (65.109.186.210)

SSH to server:
```bash
ssh root@65.109.186.210
```

Run:
```bash
# Clone
git clone https://github.com/hamismartsystems/Hami-Telegram-Proxy.git
cd Hami-Telegram-Proxy
chmod +x install.sh scripts/deploy_production.sh scripts/setup_domain_ssl.sh

# Set tokens (already saved in secrets, but set env)
export HAMI_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
export CF_TOKEN="YOUR_CF_TOKEN_HERE"

# One-click production deploy
sudo ./scripts/deploy_production.sh \
  --foreign-ip 65.109.186.210 \
  --iran-ip 65.109.186.210 \
  --cf-token $CF_TOKEN \
  --bot-token $HAMI_BOT_TOKEN

# Or manual MTProto:
docker rm -f hami-mtproto
docker run -d --name hami-mtproto --restart=always -p 443:443 \
  telegrammessenger/mtg:latest run --cloak-port 993 \
  -b 0.0.0.0:443 -4 65.109.186.210:443 eeYOUR_SECRET_HERE_1 --allow-replay

# Check logs
docker logs -f hami-mtproto

# Setup Nginx + SSL for panel and landing
sudo ./scripts/setup_domain_ssl.sh
# This will get Let's Encrypt SSL for panel.hamidesigns.shop and landing.hamidesigns.shop

# Start combined panel+bot
cat > /etc/systemd/system/hami-combined.service <<EOF
[Unit]
Description=HAMI Combined Panel+Bot+Dashboard Pro Max
After=network-online.target docker.service
Wants=network-online.target
[Service]
Type=simple
WorkingDirectory=/opt/hami-proxy
Environment=HAMI_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
Environment=HAMI_ADMIN_USER=admin
Environment=HAMI_ADMIN_PASS=Hami@2026Pro
ExecStart=/usr/bin/python3 /root/Hami-Telegram-Proxy/hami_proxy/combined_panel_bot.py
Restart=always
[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now hami-combined
systemctl status hami-combined

# Dashboard: http://65.109.186.210:8080 and https://panel.hamidesigns.shop
# Admin: https://panel.hamidesigns.shop (admin / Hami@2026Pro)
```

## Test

From your phone:
```
tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=eeYOUR_SECRET_HERE_1&bot=@HamiSmartSystems
```
Click → Telegram → Connect → Should connect

## Bot

Bot token: YOUR_BOT_TOKEN_HERE
Bot username: You need to set via @BotFather, then bot will distribute proxies

Run bot:
```bash
export HAMI_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
python3 hami_proxy/bot.py
```

## Cloudflare CDN

- Go to Cloudflare Dashboard → hamidesigns.shop → DNS
- For panel.hamidesigns.shop and landing.hamidesigns.shop, set Proxy status to Proxied (orange cloud) for CDN + DDoS protection
- For proxy.hamidesigns.shop, keep DNS only (gray cloud) for direct MTProto

## Final Links to Share

```
🚀 HAMI Telegram Proxy Pro — Anti-Filter High Speed

🔗 Google (پرسرعت):
tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=eeYOUR_SECRET_HERE_1&bot=@HamiSmartSystems

🔗 Cloudflare (ضد فیلتر):
tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=eeYOUR_SECRET_HERE_2&bot=@HamiSmartSystems

🔗 Microsoft (پایدار):
tg://proxy?server=proxy.hamidesigns.shop&port=443&secret=eeYOUR_SECRET_HERE_3&bot=@HamiSmartSystems

#HAMI #AntiFilter #HighSpeed #proxy.hamidesigns.shop
Developed by HAMI SMART SYSTEMS ❤️
```

## Monitoring

```bash
docker ps | grep hami
docker logs -f hami-mtproto
python3 hami_proxy/speed_test.py --server proxy.hamidesigns.shop --ports 443 8443 8444
```
