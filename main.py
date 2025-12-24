import os
import time
import random
import requests
from flask import Flask
from threading import Thread
from datetime import datetime, timezone

app = Flask(__name__)

@app.route("/")
def home():
    return "Sniper is LIVE"

# --- الإعدادات من Render ---
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MY_ID = os.getenv("YOUR_USER_ID")

# --- متغيرات الحالة ---
total_checks = 0
hits = 0
current_username = "في انتظار البدء..."
message_id = None

def send_monitor_embed(status="HUNTING 🎯"):
    global message_id
    payload = {
        "username": "Ultra Sniper Monitor",
        "embeds": [{
            "title": "💎 نظام المراقبة عالي الدقة",
            "description": f"✅ **الحالة:** {status}",
            "color": 0x5865F2,
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
            requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=payload)
        else:
            r = requests.post(f"{WEBHOOK_URL}?wait=true", json=payload)
            if r.status_code in [200, 201]:
                message_id = r.json().get("id")
    except: pass

def check_internal(target):
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN is missing!")
        return None
    
    url = f"https://discord.com/api/v9/users/search?query={target}"
    # هيدرز دقيقة لمحاكاة المتصفح ومنع خطأ 400
    headers = {
        "Authorization": TOKEN.strip(), # إزالة أي فراغات زائدة
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "X-Discord-Locale": "en-US"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            users = r.json().get("users", [])
            return not any(u.get("username", "").lower() == target.lower() for u in users)
        else:
            print(f"⚠️ SEARCH ERROR: {r.status_code} for {target}")
            return None
    except: return None

def worker():
    global total_checks, hits, current_username
    
    print("🚀 محاولة إرسال الإيمبد الأول...")
    time.sleep(5) # انتظار استقرار الخدمة
    send_monitor_embed()

    while True:
        # توليد اسم (3 حروف + رقم/رمز)
        target = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(3)) + random.choice("._0123456789")
        current_username = target
        total_checks += 1
        
        result = check_internal(target)
        
        if result is True:
            hits += 1
            requests.post(WEBHOOK_URL, json={
                "content": f"🎯 **صيد محتمل!** `{target}` <@{MY_ID}>"
            })
        
        # تحديث الإيمبد كل 5 عمليات فحص لتقليل الضغط
        if total_checks % 5 == 0:
            send_monitor_embed()
            
        # وقت انتظار بشري (أمان عالي)
        time.sleep(random.uniform(25, 40))

# تشغيل الخيط الخلفي
Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    # رندر يستخدم بورت 10000 تلقائياً
    app.run(host="0.0.0.0", port=10000)
