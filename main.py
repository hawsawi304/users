import requests
import time
import os
import random
import string
import threading
from flask import Flask

# إعداد سيرفر وهمي لتشغيل Web Service
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# إعدادات البوت
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def generate_random_user():
    chars = string.ascii_lowercase + string.digits + "._"
    return ''.join(random.choice(chars) for i in range(4))

def send_to_discord(user):
    embed = {
        "username": "4-Char Sniper",
        "embeds": [{
            "title": "🎯 صيد رباعي جديد!",
            "description": f"اليوزر المتاح: **{user}**",
            "color": 0x00FF7F,
            "footer": {"text": "نظام الفحص التلقائي"},
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }]
    }
    requests.post(WEBHOOK_URL, json=embed)

def check_loop():
    print("🚀 Sniper started inside Web Service...")
    while True:
        target = generate_random_user()
        url = "https://discord.com/api/v9/users/@me/pomelo-attempt"
        headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
        
        try:
            r = requests.post(url, json={"username": target}, headers=headers)
            if r.status_code == 200 and r.json().get("taken") is False:
                send_to_discord(target)
            elif r.status_code == 429:
                time.sleep(900)
        except:
            pass
        
        # انتظار عشوائي بين 5-10 دقائق
        time.sleep(random.randint(300, 600))

# تشغيل السيرفر والبوت معاً
if __name__ == "__main__":
    # تشغيل البوت في خلفية السيرفر
    t = threading.Thread(target=check_loop)
    t.start()
    # تشغيل السيرفر
    run_flask()
