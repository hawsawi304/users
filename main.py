import os
import random
import time
import requests
import threading
import datetime
from flask import Flask

app = Flask(__name__)

stats = {
    "checked": 0,
    "found": 0,
    "current": "Starting...",
    "msg_id": None,
    "status": "متصل ✅"
}

# ================== صفحة الهوم ==================
@app.route("/")
def home():
    return f"V7.4 FINAL ACTIVE - CHECKED: {stats['checked']} - FOUND: {stats['found']}"

# ================== تحديث الحالة على الديسكورد ==================
def update_status(webhook):
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار القنص V7.4 - المطور النهائي",
                    "description": f"🔍 يفحص الآن: `{stats['current']}`\n🚦 الحالة: `{stats['status']}`",
                    "color": 0x2ecc71,
                    "fields": [
                        {"name": "📊 فحص حقيقي", "value": f"`{stats['checked']}`", "inline": True},
                        {"name": "🎯 تم صيد", "value": f"`{stats['found']}`", "inline": True}
                    ],
                    "footer": {"text": "Render Auto-Check System"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }

            if stats["msg_id"] is None:
                r = requests.post(webhook + "?wait=true", json=payload, timeout=10)
                if r.status_code == 200:
                    stats["msg_id"] = r.json().get("id")
            else:
                requests.patch(f"{webhook}/messages/{stats['msg_id']}", json=payload, timeout=10)
        except:
            time.sleep(5)
        time.sleep(20)  # تحديث كل 20 ثانية لتقليل الحظر

# ================== فحص اليوزر ==================
def check_username(user, headers):
    try:
        r = requests.post(
            "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
            json={"username": user},
            headers=headers,
            timeout=5
        )
        if r.status_code == 200:
            stats["status"] = "متصل ✅"
            return "available" if r.json().get("taken") is False else "taken"
        elif r.status_code == 429:
            stats["status"] = "محظور مؤقتاً ⚠️"
            return "rate_limit"
        return "error"
    except:
        stats["status"] = "مشكلة اتصال 🌐"
        return "error"

# ================== توليد يوزر عشوائي ==================
def generate_username():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    specials = "._"
    # توليد يوزر 4 أحرف مع السماح بنقطتين أو شرطة سفلية
    user = "".join(random.choices(chars, k=3))
    user += random.choice(specials + chars)
    return user

# ================== البوت الرئيسي ==================
def sniper():
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook: 
        print("WEBHOOK_URL غير محدد")
        return

    threading.Thread(target=update_status, args=(webhook,), daemon=True).start()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    while True:
        try:
            user = generate_username()
            stats["current"] = user

            res = check_username(user, headers)

            if res == "available":
                # تأكيد مزدوج لتقليل ضياع الفرص
                time.sleep(0.5)
                if check_username(user, headers) == "available":
                    stats["found"] += 1
                    # محاولة إرسال الصيد 3 مرات
                    for _ in range(3):
                        try:
                            r_send = requests.post(webhook, json={"content": f"🎯 @everyone **يوزر متاح مؤكد:** `{user}`"}, timeout=10)
                            if r_send.status_code == 200:
                                break
                        except:
                            time.sleep(2)
                stats["checked"] += 1
            elif res == "taken":
                stats["checked"] += 1
            elif res == "rate_limit":
                stats["status"] = "معدل طلبات مرتفع ⏳"
                time.sleep(60)

            time.sleep(1.5)  # السرعة المطلوبة (1.5 ثانية) لضمان الاستقرار
        except Exception as e:
            stats["status"] = "خطأ غير متوقع ⚠️"
            time.sleep(5)

# ================== تشغيل البوت عند أول طلب ==================
started = False

@app.before_request
def start_sniper_once():
    global started
    if not started:
        started = True
        threading.Thread(target=sniper, daemon=True).start()

# ================== تشغيل السيرفر ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
