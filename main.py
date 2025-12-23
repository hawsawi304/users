import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats_lock = threading.Lock()
stats = {"c": 0, "f": 0}

@app.route('/')
def home(): return "DEBUG_MODE_ACTIVE"

def notify(webhook, user):
    payload = {"content": f"🚨 @everyone \n🎯 **صيد مؤكد!** \n✅ اليوزر: **`{user}`**"}
    try:
        r = requests.post(webhook, json=payload, timeout=10)
        print(f"📢 Notification Sent: {r.status_code}")
    except Exception as e:
        print(f"❌ Notification Failed: {e}")

def hunt(webhook):
    print("🏹 Hunter Thread Started...")
    H = {"Content-Type": "application/json"}
    while True:
        try:
            u = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": u}, headers=H, timeout=10)
            
            with stats_lock:
                stats["c"] += 1
            
            if r.status_code == 200 and r.json().get("taken") is False:
                with stats_lock:
                    stats["f"] += 1
                notify(webhook, u)
            
            # سرعة محسوبة لتجنب الـ 429
            time.sleep(0.7)
        except Exception as e:
            print(f"⚠️ Hunt Error: {e}")
            time.sleep(5)

def update_ui(webhook):
    print("📊 UI Thread Started...")
    m_id = None
    while True:
        try:
            with stats_lock:
                c, f = stats["c"], stats["f"]
            
            payload = {
                "embeds": [{
                    "title": "🛡️ رادار V36 - فحص حي",
                    "description": f"📊 فحص: `{c}` | 🎯 صيد: `{f}`",
                    "color": 0x3498db
                }]
            }
            # محاولة الإرسال فوراً بدون sleep في البداية
            r = requests.post(webhook + "?wait=true", json=payload, timeout=15)
            if r.status_code in [200, 204, 201]:
                if m_id is None: m_id = r.json().get('id')
                print(f"✅ UI Updated. Total checked: {c}")
            else:
                print(f"❌ UI Failed (Status: {r.status_code}): {r.text}")
        except Exception as e:
            print(f"⚠️ UI Loop Error: {e}")
        
        time.sleep(25)

if __name__ == "__main__":
    # تأكد من كتابة اسم المتغير بالضررط كما في Render
    url = os.getenv('WEBHOOK_URL') 
    
    if url:
        print(f"🚀 Webhook detected: {url[:30]}...")
        threading.Thread(target=update_ui, args=(url,), daemon=True).start()
        threading.Thread(target=hunt, args=(url,), daemon=True).start()
    else:
        print("🛑 CRITICAL: WEBHOOK_URL not found! Check Render Environment Variables.")

    app.run(host='0.0.0.0', port=10000)
