# HAMI Telegram Proxy — MTProto Anti-Filter Pro 🚀

**Developed by HAMI SMART SYSTEMS — ناب، حرفه‌ای، پرسرعت**

پروکسی تلگرام اختصاصی **ضد فیلتر** با **Fake-TLS**، پرسرعت، درخور برند HAMI — تانل جدا از SSH و کانفیگ‌ها

---

## ✨ چرا HAMI Proxy ناب‌ترینه؟

| ویژگی | توضیح |
|---|---|
| **MTProto + Fake-TLS** | ترافیک شبیه HTTPS به `google.com / cloudflare.com` — DPI نمی‌تونه تشخیص بده |
| **پرسرعت** | Go mtg + BBR + بهینه برای 10K+ کانکشن همزمان |
| **ضد فیلتر** | پورت 443، Cloak 993، چند دامنه جعلی، چند سکرت |
| **تانل ایران جدا** | تانل اختصاصی ایران (FRP/WireGuard) جدا از SSH — کاربر به IP ایران وصل می‌شه، تانل امن به خارج می‌ره |
| **لینک و QR** | تولید خودکار `tg://proxy` + QR کد برای اشتراک‌گذاری |
| **پنل مانیتورینگ** | وب داشبورد ترافیک، کانکشن‌ها، لاگ |
| **برند HAMI** | لوگو، نام، لینک‌های اختصاصی `#HAMI` |

---

## 🏗️ معماری

```
[کاربر داخل ایران] 
   ↓ (اتصال به IP ایران - پرسرعت داخلی)
[سرور ایران - HAMI Iran Edge] :443 
   ↓ (تانل اختصاصی رمزنگاری شده - جدا از SSH)
[سرور خارج - HAMI MTProto Pro] :443 (Fake-TLS google.com)
   ↓
[Telegram DC]
```

- **سرور خارج**: اصلی، MTProto mtg روی 443، Fake-TLS
- **سرور ایران (اختیاری)**: Edge relay، FRP client → خارج، برای سرعت داخلی + دور زدن اختلال بین‌الملل
- **تانل جدا**: پورت 5000-6000 اختصاصی، WireGuard یا FRP، رمزنگاری AES-256، جدا از تانل‌های قبلی

---

## 🚀 نصب سریع (سرور خارج - Ubuntu 22.04)

```bash
curl -fsSL https://raw.githubusercontent.com/hamismartsystems/Hami-Download-Manager/main/../hami-telegram-proxy/install.sh | bash
# یا
git clone https://github.com/hamismartsystems/Hami-Telegram-Proxy.git
cd Hami-Telegram-Proxy
chmod +x install.sh
./install.sh
```

اسکریپت:
- BBR فعال می‌کنه (سرعت)
- mtg آخرین نسخه رو دانلود می‌کنه
- 3 سکرت Fake-TLS با دامنه‌های google.com, cloudflare.com, www.microsoft.com می‌سازه
- سرویس systemd می‌سازه
- لینک‌های `tg://` رو چاپ می‌کنه

---

## 📦 نصب دستی

### 1. پیش‌نیاز
```bash
apt update && apt install -y docker.io curl openssl
```

### 2. mtg با Docker
```bash
docker run -d --name hami-mtproto --restart=always -p 443:443 \
  -v /opt/hami-proxy:/data \
  telegrammessenger/mtg:latest run --cloak-port 993 \
  -b 0.0.0.0:443 -4 YOUR_SERVER_IP:443 \
  ee<SECRET_HEX> --allow-replay
```

### 3. تولید سکرت Fake-TLS
```bash
# سکرت معمولی 32 کاراکتر hex
head /dev/urandom | tr -dc A-F0-9 | head -c32

# تبدیل به Fake-TLS با دامنه
docker run --rm telegrammessenger/mtg generate-secret -c google.com <SECRET>
# خروجی: ee... (با دامنه google.com)
```

---

## 🔗 لینک پروکسی

فرمت:
```
tg://proxy?server=YOUR_IP&port=443&secret=ee...
https://t.me/proxy?server=YOUR_IP&port=443&secret=ee...
```

مثال HAMI:
```
tg://proxy?server=1.2.3.4&port=443&secret=ee32b5f0e6a2d1c3b4a5e6f7d8c9b0a1b2c3d4e5f6a7b8c9d0e1f2&bot=@HamiSmartSystems
#HAMI #AntiFilter #HighSpeed
```

---

## 🇮🇷 تانل ایران (اختیاری - جدا)

برای کاربران داخل ایران که اتصال مستقیم به خارج کند یا اختلال دارد:

**سرور ایران:**
```bash
# نصب FRP client
./frpc -c frpc.ini
# frpc.ini:
[common]
server_addr = FOREIGN_IP
server_port = 7000
token = HAMI_SECURE_TOKEN

[hami-mtproto]
type = tcp
local_ip = 127.0.0.1
local_port = 443
remote_port = 8443
```

**سرور خارج:**
```bash
# FRP server
./frps -c frps.ini
```

کاربر به `IRAN_IP:8443` وصل می‌شه → تانل امن → `FOREIGN_IP:443` → تلگرام

این تانل **جدا** از SSH و کانفیگ‌هاست، پورت و توکن اختصاصی HAMI.

---

## 📊 پنل مانیتورینگ

```bash
python3 hami_proxy/web_dashboard.py
# http://YOUR_IP:8080
# نمایش: کانکشن فعال، ترافیک، سکرت‌ها، لاگ
```

---

## ⚡ بهینه‌سازی سرعت

- BBR: `echo 'net.core.default_qdisc=fq' >> /etc/sysctl.conf`
- افزایش ulimit: `ulimit -n 65535`
- mtg با 4 هسته: `--concurrency 4`
- پورت 443 (عبور از فایروال)

---

## 🛡️ ضد فیلتر

- Fake-TLS با دامنه‌های محبوب (google, cloudflare, microsoft)
- پورت 443 (HTTPS)
- Cloak پورت 993 (IMAPS)
- چند سکرت چرخشی
- هر سکرت دامنه متفاوت

---

## 📜 لایسنس

GPL-3.0 — HAMI SMART SYSTEMS © 2026

---

## 💬 پشتیبانی

- Website: https://hamidesigns.shop
- GitHub: https://github.com/hamismartsystems
- Telegram: @HamiSmartSystems

**دعای کاربران بدرقه راه HAMI ❤️**
