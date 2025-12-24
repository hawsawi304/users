import os
import time
import random
import requests
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "USER SNIPER IS ACTIVE 🛡️"

# --- الإعدادات من Render ---
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def check_username(target):
    # رابط البحث المخصص للحسابات البشرية
    url = f"https://discord.com/api/v9/users/search?query={target}&limit=1"
    
    headers = {
        # التوكن الشخصي يوضع هنا كما هو بدون كلمة Bot
        "Authorization": TOKEN.strip(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Discord-Locale": "en-US",
        "X-Debug-Options": "bugReporterEnabled"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=5)
        
        if r.status_code == 200:
            data = r.json()
            # إذا لم يجد مستخدمين بهذا الاسم، يعني اليوزر متاح
            if len(data.get("users", [])) == 0:
                return True
        elif r.status_code == 429:
            print("⚠️ ضغط عالي (Rate Limit)، سأنتظر دقيقتين...")
            time.sleep(120)
        elif r.status_code == 401:
            print("❌ التوكن غير صحيح أو انتهت صلاحيته!")
        return False
    except:
        return False

def run_sniper():
    print("🚀 بدأ الصيد عبر الحساب الشخصي...")
    
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": "✅ **تم التوصيل بالحساب الشخصي!** بدأ الفحص الآن..."})

    while True:
        # توليد يوزر (مثلاً: 4 حروف عشوائية)
        target = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(4))
        
        if check_username(target):
            print(f"🎯 صيد: {target}")
            if WEBHOOK_URL:
                requests.post(WEBHOOK_URL, json={
                    "content": f"🎯 **يوزر متاح للحجز!**\nالاسم: `{target}`\nرابط المطالبة: https://discord.com/settings/user-profile"
                })
        
        # وقت انتظار "بشري" (مهم جداً لحماية حسابك من التبند)
        # سينتظر بين دقيقة ودقيقتين بين كل فحص
        time.sleep(random.uniform(60, 120))

Thread(target=run_sniper, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
