import requests
import time
import os
import random
import string
from datetime import datetime
from typing import Set
from flask import Flask
from threading import Thread

# --- إعدادات السيرفر لمنع رندر من إيقاف السكربت ---
app = Flask('')

@app.route('/')
def home():
    return "Ultra Sniper is Online and Running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- إعدادات الصيد (المتغيرات من ENV) ---
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MY_ID = os.getenv("YOUR_USER_ID") # ضع الآيدي الخاص بك في ENV للمنشن

API_BASE = "https://discord.com/api/v9"
SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

checked_cache: Set[str] = set()
CACHE_LIMIT = 5000

def generate_clean_user():
    letters = string.ascii_lowercase
    digits = string.digits
    allowed_symbols = "._"
    
    # نمط 4 أزرار: 3 حروف + (رمز أو رقم)
    part1 = ''.join(random.choice(letters) for _ in range(3))
    part2 = random.choice(allowed_symbols + digits)
    
    user_list = list(part1 + part2)
    random.shuffle(user_list)
    return ''.join(user_list)

def send_to_webhook(username):
    # المنشن باستخدام الآيدي الخاص بك لضمان وصول التنبيه
    mention = f"<@{MY_ID}>" if MY_ID else "@everyone"
    
    payload = {
        "content": f"{mention} 🎯 **لقطة يوزر 4 أزرار!**",
        "username": "G-Ultra Sniper",
        "embeds": [{
            "title": "💎 يوزر نادر (Clean Pattern)",
            "description": "لم يظهر في نتائج البحث الحالية (احتمالية توفر 80%)",
            "color": 0xFF0000,
            "fields": [
                {"name": "👤 اليوزر", "value": f"**`{username}`**", "inline": True},
                {"name": "📏 الطول", "value": "4 أزرار", "inline": True},
                {"name": "📡 الحالة", "value": "Check Manually Now!", "inline": False}
            ],
            "footer": {
                "text": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Ultra Stable"
            }
        }]
    }

    for _ in range(3):
        try:
            r = SESSION.post(WEBHOOK_URL, json=payload, timeout=10)
            if r.status_code in (200, 204):
                return
            time.sleep(2)
        except requests.RequestException:
            time.sleep(2)

def search_username(target):
    url = f"{API_BASE}/users/search"
    params = {"query": target}

    try:
        r = SESSION.get(url, params=params, timeout=15)

        if r.status_code == 200:
            users = r.json().get("users", [])
            # فحص دقيق: هل اليوزر موجود بالضبط في النتائج؟
            return any(
                u.get("username", "").lower() == target.lower()
                for u in users
            )

        if r.status_code == 429:
            data = r.json() if r.headers.get("Content-Type","").startswith("application/json") else {}
            wait = float(data.get("retry_after", 60))
            print(f"⚠️ Rate limit! Waiting {wait}s")
            time.sleep(wait)
            return None

        if r.status_code == 401:
            print("❌ Token Invalid!")
            return None

    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        pass

    return None

def start_sniping():
    print("🚀 Ultra Sniper ONLINE | Starting search...")

    while True:
        target = generate_clean_user()

        if target in checked_cache:
            continue

        checked_cache.add(target)
        if len(checked_cache) > CACHE_LIMIT:
            checked_cache.clear()

        result = search_username(target)

        if result is False:
            print(f"[🔥] احتمال صيد: {target}")
            send_to_webhook(target)
        elif result is True:
            print(f"[-] مأخوذ: {target}")

        # وقت الانتظار العشوائي (20-27 ثانية) لحماية الحساب
        time.sleep(20 + random.uniform(3, 7))

if __name__ == "__main__":
    if not all([TOKEN, WEBHOOK_URL]):
        print("❌ Missing ENV variables! Check DISCORD_TOKEN and WEBHOOK_URL")
    else:
        keep_alive() # تشغيل سيرفر الويب
        start_sniping() # تشغيل الصياد
