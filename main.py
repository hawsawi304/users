import os
import random
import time
import requests
import threading
import datetime
import logging
import gc
from flask import Flask

app = Flask(__name__)

# ================== LOGGING ==================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ================== STATS ==================
stats = {
    "checked": 0,
    "found": 0,
    "current": "Starting...",
    "msg_id": None
}

# ================== HOME ==================
@app.route("/")
def home():
    return f"V7 RUNNING | CHECKED: {stats['checked']} | FOUND: {stats['found']}"

@app.route("/test/<username>")
def test_user(username):
    """اختبار يوزر معين"""
    results = []
    for i in range(3):
        res = check_username(username)
        results.append(res)
        time.sleep(2)
    
    return {
        "username": username,
        "results": results,
        "false_count": results.count(False),
        "available": results.count(False) >= 2 and results.count("error") == 0
    }

# ================== SAFE WEBHOOK ==================
def safe_webhook(webhook, content):
    """يرسل للويب هوك بدون ما يعلق الكود"""
    try:
        requests.post(webhook, json=content, timeout=10)
    except Exception as e:
        logging.error(f"Webhook failed: {e}")

# ================== DISCORD STATUS ==================
def update_status(webhook):
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 V7 USER SCANNER",
                    "description": f"🔍 يفحص الآن: `{stats['current']}`",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "📊 Checked", "value": str(stats["checked"]), "inline": True},
                        {"name": "🎯 Found", "value": str(stats["found"]), "inline": True}
                    ],
                    "footer": {"text": "Render Live"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }

            if stats["msg_id"] is None:
                r = requests.post(webhook + "?wait=true", json=payload, timeout=10)
                if r.status_code == 200:
                    stats["msg_id"] = r.json().get("id")
            else:
                requests.patch(
                    f"{webhook}/messages/{stats['msg_id']}",
                    json=payload,
                    timeout=10
                )
        except:
            pass

        time.sleep(15)

# ================== CHECK USER ==================
def check_username(user):
    """يفحص اليوزر مع معالجة أفضل للأخطاء"""
    try:
        r = requests.post(
            "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
            json={"username": user},
            timeout=15,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        
        # معالجة Rate Limit
        if r.status_code == 429:
            wait = r.json().get("retry_after", 60)
            logging.warning(f"⏳ Rate limited: waiting {wait}s")
            time.sleep(wait + 5)
            return "rate_limited"
        
        # نجح الطلب
        if r.status_code == 200:
            return r.json().get("taken", True)
        
        # أي مشكلة ثانية
        logging.error(f"⚠️ Status {r.status_code} for {user}")
        return "error"
        
    except requests.exceptions.Timeout:
        logging.error(f"⏱️ Timeout for {user}")
        return "error"
    except requests.exceptions.ConnectionError:
        logging.error(f"🔌 Connection error for {user}")
        return "error"
    except Exception as e:
        logging.error(f"❌ Exception: {e}")
        return "error"

# ================== SNIPER ==================
def sniper():
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook:
        logging.error("NO WEBHOOK URL!")
        return

    safe_webhook(webhook, {"content": "🚀 **V7 Scanner Started**"})

    threading.Thread(
        target=update_status,
        args=(webhook,),
        daemon=True
    ).start()

    chars = "abcdefghijklmnopqrstuvwxyz0123456789"

    while True:
        try:
            user = "".join(random.choices(chars, k=random.choice([3, 4])))
            stats["current"] = user
            stats["checked"] += 1
            
            # تنظيف الذاكرة كل 1000 فحص
            if stats["checked"] % 1000 == 0:
                gc.collect()
                logging.info(f"🧹 Memory cleaned at {stats['checked']}")

            results = []

            # فحص 3 مرات
            for attempt in range(3):
                res = check_username(user)
                
                # إذا جاء Rate Limit، استنى وحاول مرة ثانية
                if res == "rate_limited":
                    time.sleep(60)
                    res = check_username(user)
                
                results.append(res)
                time.sleep(random.uniform(4, 7))  # وقت عشوائي بين الفحوصات

            # حساب النتائج
            false_count = results.count(False)  # عدد المرات اللي قال متاح
            error_count = results.count("error")  # عدد الأخطاء
            
            logging.info(f"🔍 {user}: {results}")

            # ✅ إذا على الأقل مرتين قال متاح وما فيه أخطاء → أرسل
            if false_count >= 2 and error_count == 0:
                stats["found"] += 1
                logging.info(f"✅ FOUND AVAILABLE: {user}")
                safe_webhook(
                    webhook,
                    {"content": f"🎯 **USERNAME AVAILABLE:** `{user}`\n📊 Results: `{results}`"}
                )
            else:
                logging.info(f"❌ SKIPPED: {user}")

            # انتظار بين كل يوزر
            time.sleep(random.uniform(6, 10))

        except Exception as e:
            logging.error(f"💥 CRITICAL ERROR: {e}")
            safe_webhook(webhook, {"content": f"⚠️ **Error:** {e}"})
            time.sleep(30)
            continue  # استمر بدون ما توقف

# ================== START ==================
started = False

@app.before_request
def start_once():
    global started
    if not started:
        started = True
        threading.Thread(target=sniper, daemon=True).start()

# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)