#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAMI Speed Test — Test proxy latency and speed
"""
import time
import socket
import asyncio

async def test_proxy(server, port, timeout=3):
    start = time.time()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(server, port), timeout=timeout
        )
        latency = (time.time() - start) * 1000
        writer.close()
        await writer.wait_closed()
        return {"server": server, "port": port, "latency_ms": round(latency, 1), "status": "OK"}
    except Exception as e:
        return {"server": server, "port": port, "latency_ms": None, "status": f"FAIL: {e}"}

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="1.2.3.4")
    parser.add_argument("--ports", nargs="+", type=int, default=[443, 8443, 8444])
    args = parser.parse_args()

    print(f"⚡ HAMI Speed Test — {args.server}")
    for port in args.ports:
        res = await test_proxy(args.server, port)
        print(f"{res['server']}:{res['port']} — {res['status']} — {res['latency_ms']}ms")

if __name__ == "__main__":
    asyncio.run(main())
