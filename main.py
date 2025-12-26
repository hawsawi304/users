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
    return f"V7 RUNNING | CHECKED: {stats['checked']} | FOUND: {stats['found']}"

# ================== DISCORD STATUS ==================
def update_status(webhook):
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 V7 USER SCANNER",
                    "description": f"🔍 يفحص الآن: `{stats['current']}`",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "📊 Checked", "value": str(stats["checked"]), "inline": True},
                        {"name": "🎯 Found", "value": str(stats["found"]), "inline": True}
                    ],
                    "footer": {"text": "Render Live"},
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

# ================== CHECK USER ==================
def check_username(user):
    try:
        r = requests.post(
            "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
            json={"username": user},
            timeout=5
        )
        if r.status_code == 200:
            return r.json().get("taken")
    except:
        pass
    return "error"

# ================== SNIPER ==================
def sniper():
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook:
        print("NO WEBHOOK")
        return

    requests.post(
        webhook,
        json={"content": "🚀 **V7 Scanner Started**"},
        timeout=10
    )

    threading.Thread(
        target=update_status,
        args=(webhook,),
        daemon=True
    ).start()

    chars = "abcdefghijklmnopqrstuvwxyz0123456789"

    while True:
        try:
            user = "".join(random.choices(chars, k=random.choice([3, 4])))
            stats["current"] = user
            stats["checked"] += 1

            results = []

            # فحص 3 مرات للتأكيد
            for _ in range(3):
                res = check_username(user)
                results.append(res)
                time.sleep(1.5)

            # إذا ولا مرة قال محجوز → متاح مضمون
            if True not in results and "error" not in results:
                stats["found"] += 1
                print(f"[FOUND CONFIRMED] {user}")
                requests.post(
                    webhook,
                    json={"content": f"🎯 **USERNAME AVAILABLE:** `{user}`"},
                    timeout=10
                )
            else:
                print(f"[SKIPPED] {user} | {results}")

            time.sleep(2)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

# ================== START ==================
started = False

@app.before_request
def start_once():
    global started
    if not started:
        started = True
        threading.Thread(target=sniper, daemon=True).start()

# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
