import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"checked": 0, "found": 0}

@app.route('/')
def home(): return "ACTIVE"

def update_status(webhook):
    # رسالة العداد اللي تطمنك إن البوت حي
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📊 رادار القنص المباشر",
                    "description": f"✅ تم فحص: **`{stats['checked']}`** يوزر\n🎯 تم صيد: **`{stats['found']}`** يوزر",
                    "color": 0x3498db,
                    "footer": {"text": "تحديث تلقائي للنبض"}
                }]
            }
            requests.post(webhook, json=payload)
        except: pass
        time.sleep(60) # يرسل تحديث كل دقيقة عشان ترتاح

def sniper():
    webhook = os.getenv('WEBHOOK_URL')
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    social_chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    
    while True:
        try:
            # 1. ديسكورد (4 خانات)
            u_dc = "".join(random.choices(chars, k=4))
            r_dc = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", json={"username": u_dc}, timeout=5)
            stats["checked"] += 1
            if r_dc.status_code == 200 and r_dc.json().get("taken") == False:
                stats["found"] += 1
                requests.post(webhook, json={"content": f"🎯 **ديسكورد متاح:** `{u_dc}` @everyone"})

            # 2. انستقرام (5 خانات)
            u_ig = "".join(random.choices(social_chars, k=5))
            r_ig = requests.get(f"https://www.instagram.com/{u_ig}/?__a=1&__d=dis", timeout=5)
            stats["checked"] += 1
            if r_ig.status_code == 404:
                stats["found"] += 1
                requests.post(webhook, json={"content": f"📸 **انستا متاح:** `{u_ig}` @everyone"})

            # 3. تويتر (5 خانات)
            u_tw = "".join(random.choices(chars, k=5))
            r_tw = requests.get(f"https://twitter.com/{u_tw}", timeout=5)
            stats["checked"] += 1
            if r_tw.status_code == 404:
                stats["found"] += 1
                requests.post(webhook, json={"content": f"🐦 **تويتر متاح:** `{u_tw}` @everyone"})

        except: pass
        time.sleep(10)

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if webhook:
        # تشغيل العداد
        threading.Thread(target=update_status, args=(webhook,), daemon=True).start()
        # تشغيل القناص
        threading.Thread(target=sniper, daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
