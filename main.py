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
    return "Sniper Status: RUNNING 🚀"

# --- جلب البيانات من البيئة ---
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MY_ID = os.getenv("YOUR_USER_ID")

# --- متغيرات الحالة (State) ---
total_checks = 0
hits = 0
current_username = "Initializing..."
message_id = None

def send_update(status_msg="جاري البحث عن يوزرات نادرة..."):
    global message_id
    if not WEBHOOK_URL: return
    
    payload = {
        "username": "Ultra Sniper Live",
        "embeds": [{
            "title": "📡 رادار اليوزرات — تحديث مباشر",
            "description": f"ℹ️ **الحالة:** {status_msg}",
            "color": 0x5865F2,
            "fields": [
                {"name": "👤 المفحوص الآن", "value": f"`{current_username}`", "inline": True},
                {"name": "📊 إجمالي الفحص", "value": f"`{total_checks}`", "inline": True},
                {"name": "🎯 عدد الصيد", "value": f"`{hits}`", "inline": True}
            ],
            "footer": {"text": f"توقيت الخادم: {datetime.now().strftime('%H:%M:%S')} | Render Service"}
        }]
    }
    try:
        if message_id:
            requests.patch(f"{WEBHOOK_URL}/messages/{message_id}", json=payload, timeout=10)
        else:
            r = requests.post(f"{WEBHOOK_URL}?wait=true", json=payload, timeout=10)
            if r.status_code in [200, 201, 204]:
                message_id = r.json().get("id")
    except Exception as e:
        print(f"Webhook Error: {e}")

def check_username(target):
    if not TOKEN: return "NO_TOKEN"
    
    # تحويل الطلب لمحاكاة المتصفح تماماً
    url = f"https://discord.com/api/v9/users/search?query={target}&limit=1"
    
    headers = {
        "Authorization": TOKEN.strip(),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        "Context-Properties": "eyJsb2NhdGlvbiI6IkFkZCBGcmllbmQifQ==", # محاكاة "قائمة إضافة صديق"
        "X-Discord-Locale": "en-US",
        "X-Debug-Options": "bugReporterEnabled",
        "Referer": "https://discord.com/channels/@me",
        "Authority": "discord.com"
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        
        if r.status_code == 200:
            data = r.json()
            users = data.get("users", [])
            # المنطق: إذا لم نجد أي يوزر بهذا الاسم المطابق
            return not any(u.get("username", "").lower() == target.lower() for u in users)
        elif r.status_code == 400: return "BAD_REQUEST"
        elif r.status_code == 401: return "UNAUTHORIZED"
        elif r.status_code == 429: return "RATE_LIMIT"
    except: return "CONN_ERROR"
    return False

def hunter_loop():
    global total_checks, hits, current_username
    
    print("🚀 محاولة تشغيل السكربت...")
    time.sleep(10) # انتظار استقرار Render
    send_update("✅ تم ربط السكربت وبدأ الفحص")

    while True:
        # توليد يوزر: 3 حروف + (نقطة، شرطة، رقم، أو حرف رابع)
        chars = "abcdefghijklmnopqrstuvwxyz"
        extra = "._1234567890" + chars
        target = "".join(random.choice(chars) for _ in range(3)) + random.choice(extra)
        
        current_username = target
        total_checks += 1
        
        status = check_username(target)
        
        if status is True:
            hits += 1
            requests.post(WEBHOOK_URL, json={
                "content": f"🎯 **صيد محتمل (دقة 80%)!**\nالاسم: `{target}`\nالمنشن: <@{MY_ID}>"
            })
            send_update(f"✨ تم العثور على يوزر متاح: {target}")
            time.sleep(60) # استراحة بعد الصيد
            
        elif status == "BAD_REQUEST":
            print(f"❌ خطأ 400: ديسكورد رفض الطلب لـ {target}")
            if total_checks % 20 == 0:
                send_update("⚠️ تنبيه: ديسكورد يرفض بعض الطلبات (خطأ 400)")
                
        elif status == "RATE_LIMIT":
            print("⏳ تبريد... ديسكورد طلب التوقف مؤقتاً")
            time.sleep(120)

        # تحديث اللوحة كل 10 عمليات فحص
        if total_checks % 10 == 0:
            send_update()
            
        # أهم جزء: الفاصل الزمني البشري لمنع البند
        time.sleep(random.uniform(25, 45))
        
        # استراحة طويلة كل 50 فحص (محاكاة ترك الجهاز)
        if total_checks % 50 == 0:
            send_update("☕ استراحة محاكاة للبشر (10 دقائق)...")
            time.sleep(600)

# تشغيل خيط البحث
Thread(target=hunter_loop, daemon=True).start()

if __name__ == "__main__":
    # رندر يحتاج بورت 10000
    app.run(host="0.0.0.0", port=10000)
