import os, random, time, requests, threading
from flask import Flask

app = Flask(__name__)
stats_lock = threading.Lock()
stats = {"c": 0, "f": 0}

@app.route('/')
def home():
    return "BOT_STATUS: ACTIVE", 200

def hunt(webhook):
    # استخدام Session يسرع الطلبات 3 مرات أكثر من requests العادي
    session = requests.Session()
    UAs = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    
    while True:
        try:
            u = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
            headers = {
                "Content-Type": "application/json",
                "User-Agent": random.choice(UAs),
                "Referer": "https://discord.com/"
            }
            
            response = session.post(
                "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                json={"username": u}, 
                headers=headers, 
                timeout=5
            )

            # التعامل مع حظر Cloudflare والـ Rate Limit
            if response.status_code == 429:
                print("🚨 Rate Limited! Waiting 3 minutes...")
                time.sleep(180) # انتظار أطول لفك الحظر
                continue
            
            if "cf-error-details" in response.text:
                print("🛡️ Cloudflare Block detected! Cooling down...")
                time.sleep(300)
                continue

            with stats_lock:
                stats["c"] += 1
            
            if response.status_code == 200:
                data = response.json()
                if data.get("taken") is False:
                    with stats_lock:
                        stats["f"] += 1
                    # إرسال الصيد فوراً في Thread منفصل لعدم تعطيل الفحص
                    threading.Thread(target=lambda: requests.post(webhook, json={"content": f"🎯 **صيد جديد:** `{u}`"})).start()

            # سرعة الفحص (2.2 ثانية لتجنب كشف البوت)
            time.sleep(2.2)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

def update_ui(webhook):
    while True:
        try:
            with stats_lock:
                c, f = stats["c"], stats["f"]
            
            payload = {
                "embeds": [{
                    "title": "🛡️ رادار التخفي - إحصائيات حية",
                    "description": f"📊 تم فحص: `{c}`\n🎯 تم صيد: `{f}`",
                    "color": 0x27ae60,
                    "footer": {"text": "تحديث تلقائي كل 60 ثانية"}
                }]
            }
            requests.post(webhook, json=payload, timeout=10)
        except:
            pass
        time.sleep(60)

if __name__ == "__main__":
    url = os.getenv('WEBHOOK_URL')
    if url:
        # تشغيل الفحص وتحديث الإحصائيات في مسارات منفصلة
        threading.Thread(target=hunt, args=(url,), daemon=True).start()
        threading.Thread(target=update_ui, args=(url,), daemon=True).start()
    
    # Render يحتاج ربط الـ Port ديناميكياً
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
