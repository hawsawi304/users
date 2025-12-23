import requests
import time
import os
import random
import string
from datetime import datetime
from typing import Set
from flask import Flask
from threading import Thread

# ---------- KEEP ALIVE ----------
app = Flask('')

@app.route('/')
def home():
    return "Ultra Sniper Status: ONLINE & HUNTING"

# ---------- ENV ----------
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

API_BASE = "https://discord.com/api/v9"
SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
})

# ---------- STATE ----------
checked_cache: Set[str] = set()
CACHE_LIMIT = 5000
total_checks = 0
hits = 0
last_update_time = datetime.now()
webhook_message_id = None

# ---------- USER GEN ----------
def generate_clean_user():
    letters = string.ascii_lowercase
    digits = string.digits
    allowed_symbols = "._"
    part1 = ''.join(random.choice(letters) for _ in range(3))
    part2 = random.choice(allowed_symbols + digits)
    user_list = list(part1 + part2)
    random.shuffle(user_list)
    return ''.join(user_list)

# ---------- EMBED ----------
def minutes_ago(dt):
    return max(0, int((datetime.now() - dt).total_seconds() // 60))

def build_payload(latest_username=None):
    is_hit = latest_username is not None
    return {
        "content": "@everyone" if is_hit else "",
        "username": "G-Ultra Sniper Monitor",
        "embeds": [{
            "title": "💎 Ultra Sniper — Live Monitor",
            "description": f"🔥 صيد محتمل: `{latest_username}`" if is_hit else "📡 المراقبة شغالة تلقائياً",
            "color": 0xFF0000 if is_hit else 0x00FF99,
            "fields": [
                {"name": "🔎 إجمالي الفحص", "value": f"`{total_checks}`", "inline": True},
                {"name": "🎯 ضربات ناجحة", "value": f"`{hits}`", "inline": True},
                {"name": "⏱️ آخر تحديث", "value": f"قبل {minutes_ago(last_update_time)} دقيقة", "inline": False}
            ],
            "footer": {"text": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        }]
    }

def send_or_update(latest_username=None):
    global webhook_message_id, last_update_time
    payload = build_payload(latest_username)

    if webhook_message_id is None:
        r = SESSION.post(f"{WEBHOOK_URL}?wait=true", json=payload)
        if r.status_code in (200, 201, 204):
            webhook_message_id = r.json().get("id")
            last_update_time = datetime.now()
    else:
        SESSION.patch(f"{WEBHOOK_URL}/messages/{webhook_message_id}", json=payload)
        last_update_time = datetime.now()

# ---------- SEARCH ----------
def search_username(target):
    try:
        r = SESSION.get(f"{API_BASE}/users/search", params={"query": target}, timeout=15)
        if r.status_code == 200:
            return any(u.get("username","").lower() == target.lower()
                       for u in r.json().get("users", []))
        if r.status_code == 429:
            time.sleep(float(r.json().get("retry_after", 60)))
    except:
        pass
    return None

# ---------- MAIN ----------
def start_sniping():
    global total_checks, hits
    time.sleep(10)
    send_or_update()

    while True:
        target = generate_clean_user()
        if target in checked_cache:
            continue
        checked_cache.add(target)
        if len(checked_cache) > CACHE_LIMIT:
            checked_cache.clear()

        total_checks += 1
        result = search_username(target)

        if result is False:
            hits += 1
            send_or_update(target)
        elif total_checks % 5 == 0:
            send_or_update()

        time.sleep(20 + random.uniform(3, 7))

# ---------- ENTRY ----------
if __name__ == "__main__":
    if not all([TOKEN, WEBHOOK_URL]):
        raise RuntimeError("Missing ENV")
    Thread(target=start_sniping, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
