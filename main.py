import os
import time
import requests
from flask import Flask
from threading import Thread
from datetime import datetime

# ----------------- FLASK APP -----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Service is running"

# ----------------- ENV -----------------
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ----------------- EMBED SENDER -----------------
def send_embed(status="RUNNING"):
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL غير موجود في ENV")
        return

    payload = {
        "username": "Ultra Monitor",
        "embeds": [
            {
                "title": "📡 Live Embed Test",
                "description": f"الحالة الحالية: **{status}**",
                "color": 0x00FF00,
                "fields": [
                    {
                        "name": "🕒 الوقت",
                        "value": datetime.utcnow().strftime("%H:%M:%S"),
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Render Web Service"
                }
            }
        ]
    }

    try:
        r = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=10
        )

        print("📤 Webhook status code:", r.status_code)

        if r.status_code not in (200, 204):
            print("❌ Webhook response:", r.text)
        else:
            print("✅ Embed تم إرساله بنجاح")

    except Exception as e:
        print("❌ Exception أثناء الإرسال:", e)

# ----------------- BACKGROUND THREAD -----------------
def background_worker():
    print("🚀 Background worker started")
    time.sleep(10)

    while True:
        send_embed("ALIVE")
        time.sleep(60)  # يحدث كل دقيقة

# ----------------- START THREAD -----------------
Thread(target=background_worker, daemon=True).start()

# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
