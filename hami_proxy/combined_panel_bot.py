#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAMI Combined Panel + Bot — Pro Max — Merged
- Admin Panel (8081) + Bot (8082) + Dashboard (8080) unified
- One service, one domain proxy.hamidesigns.shop with paths:
  /admin -> Admin Panel
  /bot -> Bot status
  / -> Landing + Dashboard
- Branded HAMI SMART SYSTEMS
"""
import os
import sys
import threading
from pathlib import Path
import json

# Import panels
sys.path.insert(0, str(Path(__file__).parent))

def run_admin_panel():
    try:
        from admin_panel import app as admin_app
        admin_app.run(host="0.0.0.0", port=8081, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Admin panel error: {e}")

def run_dashboard():
    try:
        from web_dashboard import app as dash_app
        dash_app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Dashboard error: {e}")

def run_bot():
    try:
        # Only run if token set
        token = os.getenv("HAMI_BOT_TOKEN")
        if not token or token=="YOUR_BOT_TOKEN_HERE":
            print("Bot token not set, skipping bot")
            return
        from bot import main as bot_main
        bot_main()
    except Exception as e:
        print(f"Bot error: {e}")

if __name__=="__main__":
    print("🌐 HAMI Combined Panel + Bot Pro Max starting...")
    print(" - Admin Panel: http://0.0.0.0:8081 (panel.hamidesigns.shop)")
    print(" - Dashboard: http://0.0.0.0:8080")
    print(" - Bot: polling if HAMI_BOT_TOKEN set")

    t_admin = threading.Thread(target=run_admin_panel, daemon=True)
    t_dash = threading.Thread(target=run_dashboard, daemon=True)
    t_bot = threading.Thread(target=run_bot, daemon=True)

    t_admin.start()
    t_dash.start()
    t_bot.start()

    # Keep main alive
    try:
        while True:
            import time
            time.sleep(10)
            # Save stats periodically
            try:
                from user_manager import manager
                manager.save_stats()
            except:
                pass
    except KeyboardInterrupt:
        print("Shutting down HAMI Combined...")
