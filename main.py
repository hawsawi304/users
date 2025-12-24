import os
import random
import time
import requests
import threading
import datetime
from flask import Flask

app = Flask(__name__)

# ================== STATS ==================
stats = {
    "checked": 0,
    "found": 0,
    "current": "Starting...",
    "msg_id": None
}

# ================== HOME ROUTE ==================
@app.route("/")
def home():
    return f"V7 PRO IS RUNNING - CHECKED: {stats['checked']}"

# ================== DISCORD STATUS UPDATER ==================
def update_status(webhook):
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار القنص V7 - الحالة المباشرة",
                    "description": f"🔍 يفحص الآن: `{stats['current']}`",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "📊 تم فحص", "value": f"`{stats['checked']}`", "inline": True},
                        {"name": "🎯 تم صيد", "value": f"`{stats['found']}`", "inline": True}
                    ],
                    "footer": {"text": "Render Live Update"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }

            if stats["msg_id"] is None:
                r = requests.post(webhook + "?wait=true", json=payload, timeout=10)
                if r.status_code == 200:
                    stats["msg_id"] = r.json().get("id")
            else:
                requests.patch(
                    f"{webhook}/messages/{stats['msg_id']}",
                    json=payload,
                    timeout=10
                )
        except:
            pass

        time.sleep(15)

# ================== SNIPER ==================
def sniper():
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook:
        return

    # إشعار تشغيل
    try:
        requests.post(
            webhook,
            json={"content": "🚀 **بوت القنص V7 اشتغل بنجاح!**"},
            timeout=10
        )
    except:
        pass

    threading.Thread(
        target=update_status,
        args=(webhook,),
        daemon=True
    ).start()

    chars = "abcdefghijklmnopqrstuvwxyz0123456789"

    while True:
        try:
            user = "".join(random.choices(chars, k=4))
            stats["current"] = user

            r = requests.post(
                "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                json={"username": user},
                timeout=5
            )

            stats["checked"] += 1

            if r.status_code == 200 and r.json().get("taken") is False:
                stats["found"] += 1
                requests.post(
                    webhook,
                    json={"content": f"🎯 **يوزر متاح:** `{user}`"},
                    timeout=10
                )

            time.sleep(2)

        except:
            time.sleep(10)

# ================== START ON FIRST REQUEST ==================
started = False

@app.before_first_request
def start_sniper_once():
    global started
    if not started:
        started = True
        threading.Thread(target=sniper, daemon=True).start()
