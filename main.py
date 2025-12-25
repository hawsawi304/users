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

# ================== LOGGER ==================
def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

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
                    log("📨 Discord Status message created")
            else:
                requests.patch(
                    f"{webhook}/messages/{stats['msg_id']}",
                    json=payload,
                    timeout=10
                )
        except Exception as e:
            log(f"🔥 Status update error: {e}")

        time.sleep(15)

# ================== SNIPER ==================
def sniper():
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook:
        log("❌ WEBHOOK_URL غير موجود")
        return

    try:
        r = requests.post(
            webhook,
            json={"content": "🚀 **بوت V7 اشتغل بنجاح!**"},
            timeout=10
        )
        log(f"📨 Webhook start status: {r.status_code}")
    except Exception as e:
        log(f"❌ Webhook error: {e}")

    threading.Thread(
        target=update_status,
        args=(webhook,),
        daemon=True
    ).start()

    chars = "abcdefghijklmnopqrstuvwxyz0123456789._"

    while True:
        length = random.randint(1, 4)  # طول اليوزر من 1 إلى 4
        user = "".join(random.choices(chars, k=length))
        stats["current"] = user

        try:
            r = requests.post(
                "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                json={"username": user},
                timeout=5
            )

            stats["checked"] += 1

            # ---- RATE LIMIT ----
            if r.status_code == 429:
                log(f"⏳ RATE LIMIT - توقف 15 ثانية | user={user}")
                time.sleep(15)
                continue

            # ---- رد غير طبيعي ----
            if r.status_code != 200:
                log(f"⚠️ Status غير متوقع {r.status_code} | user={user}")
                time.sleep(2)
                continue

            try:
                data = r.json()
            except Exception as e:
                log(f"❌ JSON Error | user={user} | {e}")
                continue

            # ---- فحص النتيجة ----
            if "taken" not in data:
                log(f"⚠️ رد بدون taken | user={user} | data={data}")
                continue

            if data["taken"] is False:
                stats["found"] += 1
                log(f"🎯 AVAILABLE (first check): {user}")

                res = requests.post(
                    webhook,
                    json={"content": f"🎯 **يوزر متاح:** `{user}`"},
                    timeout=10
                )

                if res.status_code not in (200, 204):
                    log(f"❌ Webhook فشل | status={res.status_code}")

            else:
                # ---- إعادة فحص لتجنب false negative ----
                time.sleep(1)
                r2 = requests.post(
                    "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                    json={"username": user},
                    timeout=5
                )

                if r2.status_code == 200:
                    try:
                        d2 = r2.json()
                        if d2.get("taken") is False:
                            stats["found"] += 1
                            log(f"🎯 AVAILABLE (second check): {user}")

                            requests.post(
                                webhook,
                                json={"content": f"🎯 **يوزر متاح (إعادة فحص):** `{user}`"},
                                timeout=10
                            )
                    except Exception as e:
                        log(f"❌ JSON Error second check | user={user} | {e}")

            time.sleep(2)

        except Exception as e:
            log(f"🔥 Exception عام | user={user} | {e}")
            time.sleep(5)

# ================== START ON FIRST REQUEST (FLASK 3 SAFE) ==================
started = False

@app.before_request
def start_sniper_once():
    global started
    if not started:
        started = True
        threading.Thread(target=sniper, daemon=True).start()
        log("🚀 Sniper thread started")

# ================== RUN FLASK ==================
if __name__ == "__main__":
    log("🟢 Flask app starting...")
    app.run(host="0.0.0.0", port=5000)
