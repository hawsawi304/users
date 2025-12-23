import os
import time
import random
import string
import requests
from datetime import datetime
from flask import Flask
from threading import Thread

# ---------------- FLASK ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Sniper is running"

# ---------------- ENV ----------------
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

API = "https://discord.com/api/v9"
HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

# ---------------- STATE ----------------
message_id = None
total_checks = 0
hits = 0
last_update = datetime.utcnow()

# ---------------- UTILS ----------------
def minutes_ago(t):
    return int((datetime.utcnow() - t).total_seconds() // 60)

def gen_username():
    letters = string.ascii_lowercase
    extra = "._0123456789"
    return "".join(random.choice(letters) for _ in range(3)) + random.choice(extra)

# ---------------- EMBED ----------------
def build_embed(hit=None):
    desc = "🔍 الفحص شغّال"
    color = 0x00FF99

    if hit:
        desc = f"🔥 **يوزر محتمل:** `{hit}`"
        color = 0xFF0000

    return {
        "content": "@everyone" if hit else "",
        "embeds": [{
            "title": "📡 Username Sniper — Live",
            "description": desc,
            "color": color,
            "fields": [
                {"name": "🔎 إجمالي الفحص", "value": str(total_checks), "inline": True},
                {"name": "🎯 نتائج محتملة", "value": str(hits), "inline": True},
                {"name": "⏱️ آخر تحديث", "value": f"قبل {minutes_ago(last_update)} دقيقة", "inline": False}
            ],
            "footer": {"text": "Render Web Service"}
        }]
    }

def send_or_update(hit=None):
    global message_id, last_update

    payload = build_embed(hit)

    try:
        if message_id is None:
            r = requests.post(f"{WEBHOOK_URL}?wait=true", json=payload, timeout=10)
            if r.status_code in (200, 201):
                message_id = r.json()["id"]
        else:
            r = requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=payload, timeout=10)

        last_update = datetime.utcnow()

    except Exception as e:
        print("WEBHOOK ERROR:", e)

# ---------------- SEARCH ----------------
def check_username(name):
    url = f"{API}/users/search?query={name}"
    r = requests.get(url, headers=HEADERS, timeout=10)

    print("SEARCH:", r.status_code, name)

    if r.status_code == 401:
        print("❌ TOKEN INVALID")
        time.sleep(60)
        return None

    if r.status_code == 200:
        users = r.json().get("users", [])
        return not any(u["username"].lower() == name.lower() for u in users)

    if r.status_code == 429:
        time.sleep(60)

    return None

# ---------------- WORKER ----------------
def sniper():
    global total_checks, hits
    time.sleep(10)

    print("🚀 SNIPER STARTED")
    send_or_update()

    while True:
        name = gen_username()
        total_checks += 1

        result = check_username(name)

        if result is True:
            hits += 1
            send_or_update(name)
        else:
            if total_checks % 5 == 0:
                send_or_update()

        time.sleep(25)

# ---------------- START ----------------
Thread(target=sniper, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
