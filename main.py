import os
import time
import random
import requests
from flask import Flask
from threading import Thread
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "SERVER IS ONLINE 🚀"

# --- الإعدادات ---
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MY_ID = os.getenv("YOUR_USER_ID")

# --- المتغيرات العامة ---
total_checks = 0
hits = 0
current_username = "بدء التشغيل..."
message_id = None

def send_status_embed(status_text="جاري الفحص..."):
    global message_id
    if not WEBHOOK_URL: return
    
    payload = {
        "embeds": [{
            "title": "🛡️ نظام صيد اليوزرات المطور",
            "description": f"✅ **الحالة:** {status_text}",
            "color": 0x2b2d31,
            "fields": [
                {"name": "👤 المفحوص", "value": f"`{current_username}`", "inline": True},
                {"name": "📊 الإجمالي", "value": f"`{total_checks}`", "inline": True},
                {"name": "🎯 الصيد", "value": f"`{hits}`", "inline": True}
            ],
            "footer": {"text": f"آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"}
        }]
    }
    try:
        if message_id:
            requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=payload, timeout=10)
        else:
            r = requests.post(f"{WEBHOOK_URL}?wait=true", json=payload, timeout=10)
            if r.status_code in [200, 201]:
                message_id = r.json().get("id")
    except: pass

def check_username(target):
    if not TOKEN: return "NO_TOKEN"
    
    # رابط البحث الرسمي لمحاكاة الحساب الشخصي
    url = f"https://discord.com/api/v9/users/search?query={target}&limit=1"
    
    # هيدرز متطورة جداً لتخطي خطأ 400
    headers = {
        "Authorization": TOKEN.strip(),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        "Referer": "https://discord.com/channels/@me",
        "X-Discord-Locale": "en-US",
        "X-Debug-Options": "bugReporterEnabled",
        "Connection": "keep-alive"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            users = r.json().get("users", [])
            # إذا كانت القائمة فارغة يعني اليوزر متاح بنسبة كبيرة
            return len(users) == 0
        elif r.status_code == 400: return "BAD_REQUEST"
        elif r.status_code == 429: return "RATE_LIMIT"
        elif r.status_code == 401: return "AUTH_FAILED"
    except: return "ERROR"
    return False

def worker():
    global total_checks, hits, current_username
    
    time.sleep(10) # انتظار استقرار رندر
    send_status_embed("🚀 تم التشغيل بنجاح")

    while True:
        # توليد يوزر (3 حروف + رمز/رقم)
        target = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(3)) + random.choice("._0123456789")
        current_username = target
        total_checks += 1
        
        result = check_username(target)
        
        if result is True:
            hits += 1
            requests.post(WEBHOOK_URL, json={"content": f"🎯 **يوزر صيد محتمل!**\nالاسم: `{target}`\nالمنشن: <@{MY_ID}>"})
            send_status_embed(f"✨ تم صيد: {target}")
            time.sleep(10) # استراحة بعد الصيد
            
        elif result == "BAD_REQUEST":
            print(f"❌ Error 400 for {target} - Check Token")
            if total_checks % 30 == 0:
                send_status_embed("⚠️ تنبيه: مشكلة في الاستجابة (400)")
        
        elif result == "RATE_LIMIT":
            time.sleep(60) # تبريد دقيقتين
            
        # تحديث اللوحة كل 10 محاولات
        if total_checks % 10 == 0:
            send_status_embed()
            
        # وقت انتظار بشري عشوائي (ضروري جداً)
        time.sleep(random.uniform(25, 40))

# تشغيل في الخلفية
Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
