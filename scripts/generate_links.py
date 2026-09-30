#!/usr/bin/env python3
# HAMI Link Generator — Pro
import sys
sys.path.insert(0, '../hami_proxy')
from manager import generate_all
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--server", required=True)
parser.add_argument("--count", type=int, default=5)
args = parser.parse_args()

proxies = generate_all(args.server, args.count)
for p in proxies:
    print(f"{p['tg_link']}  # {p['domain']} #HAMI")
