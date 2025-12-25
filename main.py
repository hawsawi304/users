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

# ================== HOME ==================
@app.route("/")
def home():
    return f"V7 PRO IS RUNNING - CHECKED: {stats['checked']}"

# ================== DISCORD STATUS ==================
def update_status(webhook):
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار القنص V7 - الحالة المباشرة",
                    "description": f"🔍 يفحص الآن: `{stats['current']}`\n⏰ آخر تحديث: {datetime.datetime.now().strftime('%H:%M:%S')}",
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
        except Exception as e:
            print(f"[Status Error] {e}")

        time.sleep(15)

# ================== SNIPER ==================
def sniper():
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook:
        print("🚨 WEBHOOK_URL not set!")
        return

    try:
        requests.post(
            webhook,
            json={"content": "🚀 **بوت V7 اشتغل بنجاح!**"},
            timeout=10
        )
    except Exception as e:
        print(f"[Webhook Error] {e}")

    threading.Thread(
        target=update_status,
        args=(webhook,),
        daemon=True
    ).start()

    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    extra_chars = "._"

    while True:
        try:
            # طول من 3 إلى 4 فقط
            length = random.randint(3, 4)
            user = "".join(random.choices(chars + extra_chars, k=length))
            stats["current"] = user

            r = requests.post(
                "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                json={"username": user},
                timeout=5
            )

            stats["checked"] += 1

            if r.status_code == 200 and r.json().get("taken") is False:
                stats["found"] += 1
                try:
                    requests.post(
                        webhook,
                        json={"content": f"🎯 **يوزر متاح:** `{user}`"},
                        timeout=10
                    )
                except Exception as e:
                    print(f"[Webhook Post Error] {e}")

            elif r.status_code == 429:
                # Rate Limit -> توقف طويل
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ⏳ RATE LIMIT - توقف 120 ثانية | user={user}")
                time.sleep(120)
            elif r.status_code != 200:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ⚠️ Status غير متوقع {r.status_code} | user={user}")

            # فاصل بين كل محاولة لتقليل الضغط على Discord
            time.sleep(6)

        except Exception as e:
            print(f"[Sniper Error] {e}")
            time.sleep(10)

# ================== START ON FIRST REQUEST ==================
started = False

@app.before_request
def start_sniper_once():
    global started
    if not started:
        started = True
        threading.Thread(target=sniper, daemon=True).start()

# ================== RUN FLASK ==================
if __name__ == "__main__":
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 🟢 Flask app starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
