import os, random, time, requests, threading
from flask import Flask

app = Flask('')
stats_lock = threading.Lock()
stats = {"c": 0, "f": 0}

@app.route('/')
def home(): return "ANTI_CLOUDFLARE_MODE"

def hunt(webhook):
    # قائمة يوزر أجينت متنوعة لتمويه الحماية
    UAs = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    
    while True:
        try:
            u = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
            headers = {"Content-Type": "application/json", "User-Agent": random.choice(UAs)}
            
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": u}, headers=headers, timeout=10)
            
            # أهم جزء: اكتشاف حماية Cloudflare
            if r.status_code == 429 or "cf-error-details" in r.text:
                print("🚨 Cloudflare Blocked us! Sleeping for 5 minutes...")
                time.sleep(300) # ارقد 5 دقائق عشان ما يطردونا نهائياً
                continue

            with stats_lock:
                stats["c"] += 1
            
            if r.status_code == 200 and r.json().get("taken") is False:
                with stats_lock:
                    stats["f"] += 1
                requests.post(webhook, json={"content": f"🚨 @everyone \n🎯 صيد رباعي: `{u}`"})
            
            # سرعة "آمنة" (فحص كل ثانيتين)
            time.sleep(2.1)
            
        except Exception as e:
            time.sleep(10)

def update_ui(webhook):
    m_id = None
    while True:
        try:
            with stats_lock:
                c, f = stats["c"], stats["f"]
            payload = {"embeds": [{"title": "🛡️ رادار التخفي V37", "description": f"📊 فحص: `{c}` | 🎯 صيد: `{f}`", "color": 0xe74c3c}]}
            r = requests.post(webhook + "?wait=true", json=payload, timeout=15)
            if m_id is None and r.status_code == 200: m_id = r.json().get('id')
            elif m_id: requests.patch(f"{webhook}/messages/{m_id}", json=payload)
        except: pass
        time.sleep(30)

if __name__ == "__main__":
    url = os.getenv('WEBHOOK_URL')
    if url:
        threading.Thread(target=update_ui, args=(url,), daemon=True).start()
        threading.Thread(target=hunt, args=(url,), daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
