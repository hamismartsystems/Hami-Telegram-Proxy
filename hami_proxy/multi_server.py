#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAMI Multi-Server Manager — Pro
- Manages multiple foreign servers for load balancing
- Auto health check, failover, round-robin DNS
- Branded HAMI SMART SYSTEMS
"""
import json
import time
import asyncio
import random
from pathlib import Path

SERVERS_FILE = Path("/opt/hami-proxy/servers.json")

DEFAULT_SERVERS = [
    {"id":1, "ip":"1.2.3.4", "location":"DE", "weight":100, "status":"online"},
    {"id":2, "ip":"5.6.7.8", "location":"FI", "weight":100, "status":"online"},
    {"id":3, "ip":"9.10.11.12", "location":"TR", "weight":80, "status":"online"},
]

class MultiServerManager:
    def __init__(self):
        self.servers = self.load()

    def load(self):
        if SERVERS_FILE.exists():
            return json.loads(SERVERS_FILE.read_text())
        return DEFAULT_SERVERS

    def save(self):
        SERVERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SERVERS_FILE.write_text(json.dumps(self.servers, indent=2), encoding="utf-8")

    async def health_check(self, server):
        # simple TCP check to 443
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(server["ip"], 443), timeout=3
            )
            writer.close()
            await writer.wait_closed()
            server["status"] = "online"
            server["last_check"] = time.time()
            return True
        except Exception as e:
            server["status"] = f"offline: {e}"
            server["last_check"] = time.time()
            return False

    async def check_all(self):
        for s in self.servers:
            await self.health_check(s)
        self.save()
        return self.servers

    def get_best_server(self):
        online = [s for s in self.servers if s["status"]=="online"]
        if not online:
            return random.choice(self.servers) if self.servers else None
        # weighted random
        total = sum(s["weight"] for s in online)
        r = random.randint(0, total-1)
        upto = 0
        for s in online:
            if upto + s["weight"] > r:
                return s
            upto += s["weight"]
        return online[0]

    def generate_balanced_links(self, secret):
        # generate links for all servers with same secret
        links = []
        for s in self.servers:
            if s["status"]=="online":
                links.append({
                    "server": s["ip"],
                    "location": s["location"],
                    "link": f"tg://proxy?server={s['ip']}&port=443&secret={secret}&bot=@HamiSmartSystems #HAMI {s['location']}"
                })
        return links

if __name__=="__main__":
    import asyncio
    m = MultiServerManager()
    print("Checking servers...")
    asyncio.run(m.check_all())
    print(json.dumps(m.servers, indent=2))
    best = m.get_best_server()
    print(f"Best: {best}")
