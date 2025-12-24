import os
import time
import random
import requests
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "4-Letter Sniper Active 🛡️"

# --- الـ Env المطلوبة في Render ---
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_to_webhook(target):
    # تنسيق الإيمبد (Embed) بدون ما يخرب السكربت
    embed = {
        "username": "User Sniper",
        "embeds": [{
            "title": "🎯 صيد رباعي جديد!",
            "description": f"اليوزر متاح حالياً: `{target}`",
            "color": 5763719,  # لون أخضر
            "fields": [
                {"name": "عدد الحروف", "value": "4", "inline": True},
                {"name": "الرابط", "value": f"[حجز اليوزر](https://discord.com/settings/user-profile)", "inline": True}
            ],
            "footer": {"text": "تم الصيد بواسطة نظام 22/12 المطور"}
        }]
    }
    requests.post(WEBHOOK_URL, json=embed)

def check_username(user):
    # الطريقة اللي كانت شغالة الساعة 9 (طريقة الـ search)
    url = f"https://discord.com/api/v9/users/search?query={user}&limit=1"
    headers = {
        "Authorization": TOKEN.strip() if TOKEN else "",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if not data.get("users"):
                return True
        elif r.status_code == 429:
            time.sleep(120) # حماية من الـ Rate Limit
        return False
    except:
        return False

def run_sniper():
    print("🚀 تم تشغيل نسخة 22/12 المحدثة (4 حروف فقط)...")
    while True:
        # تثبيت الصيد على 4 حروف بالضبط (مزيج حروف وأرقام)
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        target = "".join(random.choice(chars) for _ in range(4))
        
        if check_username(target):
            send_to_webhook(target)
        
        # حماية الحساب (وقت انتظار متغير بين 60 و 120 ثانية)
        time.sleep(random.uniform(60, 120))

Thread(target=run_sniper, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
