# HAMI Anti-Filter Techniques — Pro

## Why Telegram blocked in Iran?
- DPI (Deep Packet Inspection) detects MTProto
- Port blocking
- IP blocking

## HAMI Solutions

### 1. Fake-TLS (ee secret)
Traffic looks like HTTPS to google.com:
```
ClientHello SNI: google.com
ServerHello: real TLS handshake
Then: MTProto inside TLS Application Data
```
DPI sees: `google.com` HTTPS, not proxy.

Generate:
```bash
mtg generate-secret -c google.com <32hex>
# ee + secret + hex(google.com)
```

### 2. Port 443 + Cloak 993
- 443 is HTTPS, rarely blocked
- 993 is IMAPS, used as cloak to confuse DPI

### 3. Multiple secrets + domains
- If one secret blocked, others work
- Different fake domains: google, cloudflare, microsoft

### 4. Iran Tunnel Separate
- Domestic connection to Iran IP is fast and not filtered internationally
- Iran edge -> Foreign via encrypted FRP/WireGuard tunnel
- User: Iran IP:8443 (domestic) -> tunnel -> Foreign:443 -> Telegram

### 5. BBR + TCP optimization
- BBR congestion control for high packet loss
- `net.ipv4.tcp_fastopen = 3`

### 6. Future: Domain Fronting via CDN
- Use Cloudflare CDN to front proxy
