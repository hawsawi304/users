import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
# قفل لحماية البيانات من الـ Race Condition
stats_lock = threading.Lock()
stats = {"c": 0, "f": 0}

@app.route('/')
def home(): return "LOGIC_STABILITY_V35"

H = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
}

def notify(webhook, user):
    """منطق إرسال منفصل مع التحقق من النجاح"""
    payload = {"content": f"🚨 @everyone \n🎯 **صيد مؤكد!** \n✅ اليوزر: **`{user}`**"}
    for attempt in range(3): # محاولة الإرسال حتى 3 مرات في حال الفشل
        try:
            r = requests.post(webhook, json=payload, timeout=10)
            if r.status_code in [200, 204]:
                return True
            elif r.status_code == 429: # Rate limit على الويبهوك نفسه
                time.sleep(r.json().get('retry_after', 1))
        except Exception as e:
            print(f"Webhook Error: {e}")
        time.sleep(2)
    return False

def hunt(webhook):
    while True:
        try:
            u = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": u}, headers=H, timeout=7)
            
            # حماية التحديث باستخدام القفل
            with stats_lock:
                stats["c"] += 1
            
            if r.status_code == 200:
                data = r.json()
                # تحقق صارم من النتيجة
                if data.get("taken") is False:
                    with stats_lock:
                        stats["f"] += 1
                    # إرسال التنبيه فوراً
                    notify(webhook, u)
            
            elif r.status_code == 429:
                wait_time = r.json().get('retry_after', 30)
                time.sleep(wait_time)
            
            time.sleep(0.6) # سرعة متزنة
            
        except requests.exceptions.RequestException as e:
            print(f"Network Error: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"Logic Error: {e}")
            time.sleep(2)

def update_ui(webhook):
    m_id = None
    while True:
        try:
            # قراءة آمنة للبيانات أثناء التحديث
            with stats_lock:
                current_c = stats["c"]
                current_f = stats["f"]
            
            payload = {
                "embeds": [{
                    "title": "🛡️ رادار المنطق الآمن (V35)",
                    "description": f"📊 فحص: `{current_c}` | 🎯 صيد مؤكد: `{current_f}`",
                    "color": 0x2ecc71,
                    "footer": {"text": "Thread-Safe & Error Handling Active"}
                }]
            }
            if m_id is None:
                r = requests.post(webhook + "?wait=true", json=payload, timeout=10)
                m_id = r.json().get('id')
            else:
                requests.patch(f"{webhook}/messages/{m_id}", json=payload, timeout=10)
        except: pass
        time.sleep(20)

if __name__ == "__main__":
    url = os.getenv('WEBHOOK_URL')
    if url:
        # تشغيل المسارات مع ضمان الاستقلالية
        threading.Thread(target=update_ui, args=(url,), daemon=True).start()
        threading.Thread(target=hunt, args=(url,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
