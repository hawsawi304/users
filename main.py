import os
import time
import random
import requests
import threading
import datetime
import logging
import gc
from flask import Flask
from collections import deque

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
    "current": "---",
    "errors": 0,
    "rate_limits": 0,
    "retries": 0
}

# قائمة اليوزرات اللي نبي نعيد فحصها
retry_queue = deque(maxlen=1000)

# ================== FLASK ROUTES ==================
@app.route("/")
def home():
    return f"V8 RUNNING | CHECKED: {stats['checked']} | FOUND: {stats['found']} | ERRORS: {stats['errors']} | RETRIES: {len(retry_queue)}"

@app.route("/stats")
def full_stats():
    return {
        "checked": stats["checked"],
        "found": stats["found"],
        "errors": stats["errors"],
        "rate_limits": stats["rate_limits"],
        "retries_pending": len(retry_queue),
        "current": stats["current"]
    }

# ================== SAFE WEBHOOK ==================
def safe_webhook(webhook, content):
    """يرسل للويب هوك بدون ما يعلق الكود"""
    for attempt in range(3):
        try:
            logging.info(f"📤 Sending webhook (attempt {attempt+1})...")
            r = requests.post(webhook, json=content, timeout=10)
            if r.status_code == 200:
                logging.info(f"✅ Webhook sent successfully")
                return True
            else:
                logging.warning(f"⚠️ Webhook returned {r.status_code}")
        except Exception as e:
            logging.error(f"❌ Webhook attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return False

# ================== DISCORD STATUS ==================
def update_status(webhook):
    logging.info("📊 Status updater thread started")
    while True:
        try:
            time.sleep(300)
            now = datetime.datetime.now().strftime("%H:%M")
            requests.post(
                webhook,
                json={
                    "embeds": [{
                        "title": "📊 Scanner V8 Status",
                        "color": 3447003,
                        "fields": [
                            {"name": "✅ Checked", "value": f"`{stats['checked']}`", "inline": True},
                            {"name": "🎯 Found", "value": f"`{stats['found']}`", "inline": True},
                            {"name": "🔍 Current", "value": f"`{stats['current']}`", "inline": True},
                            {"name": "⚠️ Errors", "value": f"`{stats['errors']}`", "inline": True},
                            {"name": "⏳ Rate Limits", "value": f"`{stats['rate_limits']}`", "inline": True},
                            {"name": "🔄 Retry Queue", "value": f"`{len(retry_queue)}`", "inline": True}
                        ],
                        "footer": {"text": f"Updated at {now}"}
                    }]
                },
                timeout=10
            )
        except Exception as e:
            logging.error(f"❌ Status update failed: {e}")

# ================== CHECK USER (IMPROVED) ==================
def check_username(user, attempt_num=1):
    """يفحص اليوزر مع معالجة متقدمة"""
    logging.info(f"🔍 [{attempt_num}] Checking: {user}")
    
    for retry in range(3):  # 3 محاولات لكل فحص
        try:
            r = requests.post(
                "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                json={"username": user},
                timeout=20,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                    "Accept-Language": "en-US,en;q=0.9"
                }
            )
            
            # Rate Limit
            if r.status_code == 429:
                stats["rate_limits"] += 1
                retry_after = r.json().get("retry_after", 60)
                logging.warning(f"⏳ Rate limited: waiting {retry_after}s")
                time.sleep(retry_after + random.uniform(5, 10))
                continue  # حاول مرة ثانية
            
            # Success
            if r.status_code == 200:
                taken = r.json().get("taken", True)
                logging.info(f"✅ {user} -> taken={taken}")
                return taken
            
            # أي خطأ ثاني
            if r.status_code in [500, 502, 503, 504]:
                logging.warning(f"⚠️ Server error {r.status_code}, retrying...")
                time.sleep(5)
                continue
            
            # خطأ غريب
            logging.error(f"⚠️ Unexpected status {r.status_code} for {user}")
            stats["errors"] += 1
            return None
        
        except requests.exceptions.Timeout:
            logging.warning(f"⏱️ Timeout on retry {retry+1}/3 for {user}")
            time.sleep(5)
            continue
        
        except requests.exceptions.ConnectionError:
            logging.warning(f"🔌 Connection error on retry {retry+1}/3 for {user}")
            time.sleep(10)
            continue
        
        except Exception as e:
            logging.error(f"❌ Unexpected error for {user}: {e}")
            time.sleep(5)
            continue
    
    # فشلت كل المحاولات
    stats["errors"] += 1
    logging.error(f"💀 All retries failed for {user}")
    return None

# ================== SNIPER (V8) ==================
def sniper():
    logging.info("🚀 V8 Sniper starting...")
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook:
        logging.error("❌ NO WEBHOOK URL!")
        return

    safe_webhook(webhook, {"content": "🚀 **V8 Scanner Started - Enhanced Edition**"})

    threading.Thread(target=update_status, args=(webhook,), daemon=True).start()

    chars = "abcdefghijklmnopqrstuvwxyz0123456789_"
    
    while True:
        try:
            # أولاً: شوف إذا فيه يوزرات قديمة نبي نعيد فحصها
            if retry_queue:
                user = retry_queue.popleft()
                stats["retries"] += 1
                logging.info(f"🔄 Retrying queued username: {user}")
            else:
                # ولّد يوزر جديد
                user = "".join(random.choices(chars, k=random.choice([3, 4])))
                stats["checked"] += 1
            
            stats["current"] = user
            
            # تنظيف الذاكرة
            if stats["checked"] % 1000 == 0:
                gc.collect()
                logging.info(f"🧹 Memory cleaned at {stats['checked']}")
            
            # ✨ الفحص الجديد: مرة واحدة فقط!
            result = check_username(user)
            
            # لو فشل الفحص (None) -> حطه بالقائمة
            if result is None:
                if user not in retry_queue:
                    retry_queue.append(user)
                    logging.warning(f"🔄 Added {user} to retry queue")
                time.sleep(random.uniform(10, 15))
                continue
            
            # ✅ متاح! أرسل فوراً
            if result == False:
                stats["found"] += 1
                logging.info(f"🎯🎯🎯 AVAILABLE: {user}")
                safe_webhook(
                    webhook,
                    {
                        "content": f"@everyone",
                        "embeds": [{
                            "title": "🎯 USERNAME AVAILABLE",
                            "description": f"**`{user}`**",
                            "color": 65280,
                            "fields": [
                                {"name": "Status", "value": "✅ Available", "inline": True},
                                {"name": "Length", "value": f"`{len(user)}`", "inline": True}
                            ],
                            "timestamp": datetime.datetime.utcnow().isoformat()
                        }]
                    }
                )
            else:
                logging.debug(f"❌ {user} is taken")
            
            # انتظار عشوائي
            time.sleep(random.uniform(3, 6))

        except KeyboardInterrupt:
            logging.info("🛑 Stopped by user")
            break
        except Exception as e:
            stats["errors"] += 1
            logging.error(f"💥 CRITICAL: {e}")
            safe_webhook(webhook, {"content": f"⚠️ **Critical Error:** `{e}`"})
            time.sleep(30)

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
    logging.info(f"🌐 Starting V8 on port {port}")
    app.run(host="0.0.0.0", port=port)