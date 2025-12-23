import requests
import time
import os
import random
import string
from flask import Flask
from threading import Thread

# ===== Flask App (مهم لـ Render + gunicorn) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Sniper is Active"

# ===== ENV =====
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MY_ID = os.getenv("YOUR_USER_ID")

print("=== ENV CHECK ===")
print("TOKEN:", "OK" if TOKEN else "MISSING")
print("WEBHOOK_URL:", "OK" if WEBHOOK_URL else "MISSING")
print("MY_ID:", "OK" if MY_ID else "MISSING")
print("=================")

# ===== Sniper =====
def start_sniping():
    time.sleep(10)
    print("🚀 SNIPER STARTED")

    # اختبار الويبهوك
    try:
        r = requests.post(
            WEBHOOK_URL,
            json={"content": "✅ Webhook test message"},
            timeout=10
        )
        print("WEBHOOK TEST STATUS:", r.status_code)
    except Exception as e:
        print("❌ WEBHOOK ERROR:", e)
        return

    while True:
        target = ''.join(random.choice(string.ascii_lowercase) for _ in range(3)) + random.choice("._0123456789")
        headers = {"Authorization": TOKEN}
        url = f"https://discord.com/api/v9/users/search?query={target}"

        try:
            res = requests.get(url, headers=headers, timeout=10)
            print("SEARCH STATUS:", res.status_code, "TARGET:", target)

            if res.status_code == 200:
                users = res.json().get("users", [])
                if not any(u.get("username", "").lower() == target.lower() for u in users):
                    payload = {
                        "content": f"<@{MY_ID}> 🎯 Available: `{target}`",
                        "username": "Ultra Sniper"
                    }
                    wh = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                    print("SEND RESULT:", wh.status_code)

            elif res.status_code == 401:
                print("❌ TOKEN INVALID")
                break

            elif res.status_code == 429:
                print("⏳ RATE LIMITED")
                time.sleep(60)

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        time.sleep(25)

# ===== Start background thread =====
thread = Thread(target=start_sniping)
thread.daemon = True
thread.start()

# ===== Local run only =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
