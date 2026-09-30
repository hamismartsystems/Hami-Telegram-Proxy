# HAMI High Speed Optimization

## 1. BBR
```bash
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p
```

## 2. ulimit
```bash
ulimit -n 65535
# /etc/security/limits.conf:
* soft nofile 65535
* hard nofile 65535
```

## 3. mtg concurrency
```bash
mtg run --concurrency 4 ... # 4 cores
```

## 4. Server location
- Best for Iran users: Turkey, Finland, Netherlands, Germany
- Low latency + high bandwidth

## 5. Iran tunnel
- Domestic RTT to Iran server: ~20ms
- Iran->Foreign via optimized tunnel: ~60ms
- Total ~80ms vs direct 150ms with packet loss

## 6. Monitoring
- Dashboard shows active connections
- Auto-restart on failure
