import requests
import time
import os
import random
import string

# الإعدادات - سيتم جلبها من Render لاحقاً
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ICON_URL = "https://cdn-icons-png.flaticon.com/512/893/893257.png" 

def generate_random_user():
    # يولد يوزر 4 أحرف (حروف، أرقام، نقطة، اندر سكور)
    chars = string.ascii_lowercase + string.digits + "._"
    return ''.join(random.choice(chars) for i in range(4))

def send_to_discord(user):
    embed = {
        "username": "4-Char Sniper",
        "avatar_url": ICON_URL,
        "embeds": [{
            "title": "🎯 صيد رباعي جديد!",
            "description": f"تم العثور على يوزر متاح مكون من 4 أحرف.",
            "color": 0x00FF7F,
            "fields": [
                {"name": "👤 اليوزر", "value": f"`{user}`", "inline": True},
                {"name": "🛡️ الحالة", "value": "متاح للتسجيل ✅", "inline": False}
            ],
            "footer": {"text": "نظام الفحص التلقائي", "icon_url": ICON_URL},
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }]
    }
    requests.post(WEBHOOK_URL, json=embed)

def check():
    target = generate_random_user()
    url = "https://discord.com/api/v9/users/@me/pomelo-attempt"
    headers = {
        "Authorization": TOKEN, 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        r = requests.post(url, json={"username": target}, headers=headers)
        if r.status_code == 200:
            # ديسكورد أحياناً يرد بـ 200 بس يكون اليوزر مأخوذ (taken)
            if r.json().get("taken") is False:
                send_to_discord(target)
                print(f"✅ Found: {target}")
        elif r.status_code == 429:
            print("⚠️ Rate limit! Sleeping 15m...")
            time.sleep(900)
    except:
        pass

print("🚀 Sniper started...")
while True:
    check()
    # انتظار عشوائي بين 5 لـ 10 دقائق للأمان
    time.sleep(random.randint(300, 600))
