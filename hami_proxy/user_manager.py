#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAMI User Manager — Pro user management for Telegram Proxy
- Track connections per secret
- Limit, ban, stats
- Branded
"""
import json
import time
from pathlib import Path
from collections import defaultdict, Counter

LOG_PATH = Path("/var/log/hami-proxy.log")
STATS_PATH = Path("/opt/hami-proxy/stats.json")

class UserManager:
    def __init__(self):
        self.connections = Counter()
        self.traffic = defaultdict(int)  # secret -> bytes
        self.banned = set()
        self.start_time = time.time()

    def log_connect(self, secret, ip):
        self.connections[secret] += 1
        # log
        with open(LOG_PATH, "a") as f:
            f.write(f"{time.time()} CONNECT {secret[:8]}... {ip}\n")

    def log_traffic(self, secret, bytes_count):
        self.traffic[secret] += bytes_count

    def ban_secret(self, secret):
        self.banned.add(secret)

    def get_stats(self):
        return {
            "uptime": int(time.time() - self.start_time),
            "total_connections": sum(self.connections.values()),
            "unique_secrets": len(self.connections),
            "traffic_per_secret": dict(self.traffic),
            "connections_per_secret": dict(self.connections),
            "banned_count": len(self.banned),
        }

    def save_stats(self):
        STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATS_PATH.write_text(json.dumps(self.get_stats(), indent=2), encoding="utf-8")

# Singleton
manager = UserManager()

if __name__ == "__main__":
    print(json.dumps(manager.get_stats(), indent=2))
