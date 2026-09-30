# HAMI Iran Tunnel — جدا از SSH و کانفیگ‌ها

## هدف
کاربران داخل ایران گاهی اتصال مستقیم به سرور خارج کند یا دچار اختلال بین‌الملل است.
با تانل ایران، کاربر به **IP ایران** (پرسرعت داخلی، 20ms) وصل می‌شود، سپس تانل رمزنگاری شده اختصاصی به سرور خارج می‌رود.

این تانل **جدا** از تانل‌های SSH و VLESS شماست — پورت، توکن، سرویس جدا.

## معماری
```
User (IR) -> Iran Edge 1.1.1.1:8443 (FRP client)
                |
                |---[FRP Tunnel TLS AES-256 port 7000 token HAMI_SECURE]--->
                |
Foreign 2.2.2.2:7000 (FRP server) -> 127.0.0.1:443 (mtg)
                |
                -> Telegram
```

## نصب سرور خارج (FRP Server)

```bash
wget https://github.com/fatedier/frp/releases/download/v0.52.3/frp_0.52.3_linux_amd64.tar.gz
tar xzf frp_*.tar.gz
cd frp_*

cat > frps.ini <<EOF
[common]
bind_port = 7000
token = HAMI_SECURE_TOKEN_123
dashboard_port = 7500
dashboard_user = hami
dashboard_pwd = HAMI_DASH_123
EOF

./frps -c frps.ini
# systemd:
# /etc/systemd/system/hami-frp-server.service
```

## نصب سرور ایران (FRP Client)

```bash
cat > frpc.ini <<EOF
[common]
server_addr = FOREIGN_IP
server_port = 7000
token = HAMI_SECURE_TOKEN_123
tls_enable = true

[hami-mtproto]
type = tcp
local_ip = 127.0.0.1
local_port = 443
remote_port = 8443
use_encryption = true
use_compression = true
EOF

./frpc -c frpc.ini
```

## کاربر

به جای `FOREIGN_IP:443` به `IRAN_IP:8443` وصل می‌شود — همان سکرت.

```
tg://proxy?server=IRAN_IP&port=8443&secret=ee...
```

## مزایا
- سرعت داخلی بالا
- دور زدن اختلال بین‌الملل
- IP ایران فیلتر نیست برای اتصال داخلی
- تانل جدا — امن

## جایگزین: WireGuard

برای سرعت بیشتر، به جای FRP از WireGuard استفاده کن:

```bash
# Foreign
wg genkey | tee privatekey | wg pubkey > publickey
# Iran similar
```

سپس Iran Edge ترافیک 8443 را از طریق WG تانل به Foreign فوروارد می‌کند.

## امنیت
- توکن جدا
- TLS
- فقط پورت 8443 باز
