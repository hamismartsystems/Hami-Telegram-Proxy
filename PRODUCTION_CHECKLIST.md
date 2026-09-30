# HAMI Telegram Proxy — Production Checklist — Pro

## قبل از انتشار عمومی

- [ ] سرور خارج: Ubuntu 22.04, 2GB RAM, 1TB bandwidth, DE/FI/TR
- [ ] BBR فعال
- [ ] پورت 443 باز
- [ ] mtg آخرین نسخه
- [ ] 3 سکرت Fake-TLS با دامنه‌های متفاوت
- [ ] تست لینک‌ها با تلگرام واقعی
- [ ] QR کد تولید
- [ ] پنل داشبورد روی 8080 با پسورد
- [ ] ربات تلگرام با BOT_TOKEN
- [ ] تانل ایران (اختیاری) تست
- [ ] بک‌آپ secrets.txt در جای امن
- [ ] لاگ‌ها به /var/log/hami-proxy.log
- [ ] systemd enable

## انتشار

- [ ] لینک‌ها در کانال تلگرام HAMI
- [ ] آموزش اتصال
- [ ] هشتگ #HAMI #AntiFilter

## مانیتورینگ

- [ ] docker logs -f hami-mtproto
- [ ] python3 hami_proxy/web_dashboard.py
- [ ] Uptime Kuma برای مانیتور 443

## مقیاس‌پذیری

- برای 10K+ کاربر: 2 سرور mtg با Load Balancer
- برای 100K+: چند IP + Round Robin DNS
