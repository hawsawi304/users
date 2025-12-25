import os
import random
import time
import threading
import requests
import datetime
import logging
from flask import Flask

# ================== LOGGING ==================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

# ================== APP ==================
app = Flask(__name__)

PORT = int(os.getenv("PORT", 10000))
WEBHOOK = os.getenv("WEBHOOK_URL")

# ================== STATS ==================
stats = {
    "checked": 0,
    "found": 0,
    "current": "-"
}

# ================== HOME ==================
@app.route("/")
def home():
    return f"RUNNING | CHECKED={stats['checked']} | FOUND={stats['found']}"

# ================== DISCORD STATUS ==================
def update_status():
    if not WEBHOOK:
        return

    msg_id = None

    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 V7 STATUS",
                    "description": f"🔍 Current: `{stats['current']}`",
                    "color": 0x2ecc71,
                    "fields": [
                        {"name": "Checked", "value": str(stats['checked']), "inline": True},
                        {"name": "Found", "value": str(stats['found']), "inline": True}
                    ],
                    "footer": {
                        "text": "Last update"
                    },
                    "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
                }]
            }

            if msg_id is None:
                r = requests.post(WEBHOOK + "?wait=true", json=payload, timeout=10)
                if r.status_code == 200:
                    msg_id = r.json()["id"]
                    logging.info("📨 Discord status message created")
            else:
                requests.patch(f"{WEBHOOK}/messages/{msg_id}", json=payload, timeout=10)

        except Exception as e:
            logging.warning(f"Status error: {e}")

        time.sleep(20)

# ================== SNIPER ==================
def sniper():
    logging.info("🚀 Sniper started")

    if WEBHOOK:
        requests.post(WEBHOOK, json={"content": "🚀 **BOT STARTED**"}, timeout=10)

    chars = "abcdefghijklmnopqrstuvwxyz0123456789._"

    while True:
        try:
            user = "".join(random.choices(chars, k=4))
            stats["current"] = user

            r = requests.post(
                "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                json={"username": user},
                timeout=10
            )

            stats["checked"] += 1

            if r.status_code == 200:
                if r.json().get("taken") is False:
                    stats["found"] += 1
                    logging.info(f"🎯 FOUND: {user}")
                    if WEBHOOK:
                        requests.post(
                            WEBHOOK,
                            json={"content": f"🎯 **AVAILABLE:** `{user}`"},
                            timeout=10
                        )
                else:
                    logging.info(f"❌ TAKEN: {user}")

            elif r.status_code == 429:
                logging.warning(f"⏳ RATE LIMIT → sleep 60s | user={user}")
                time.sleep(60)

            else:
                logging.warning(f"⚠️ STATUS {r.status_code} | user={user}")

            time.sleep(3)

        except Exception as e:
            logging.error(f"💥 ERROR: {e}")
            time.sleep(10)

# ================== START THREADS ON BOOT ==================
threading.Thread(target=sniper, daemon=True).start()
threading.Thread(target=update_status, daemon=True).start()

# ================== RUN ==================
if __name__ == "__main__":
    logging.info("🟢 Flask app starting...")
    app.run(host="0.0.0.0", port=PORT)
