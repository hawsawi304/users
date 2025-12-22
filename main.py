import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {
    "discord": {"checked": 0, "found": 0, "current": "...", "msg_id": None},
    "instagram": {"checked": 0, "found": 0, "current": "...", "msg_id": None},
    "twitter": {"checked": 0, "found": 0, "current": "...", "msg_id": None}
}

@app.route('/')
def home(): return "BACK_TO_ORIGIN_STABLE"

# الرؤوس البسيطة اللي اشتغلت أول مرة
HEADERS = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"}

def update_ui(webhook, platform, color, icon):
    while True:
        try:
            s = stats[platform]
            payload = {
                "embeds": [{
                    "title": f"📡 رادار {platform.upper()}",
                    "thumbnail": {"url": icon},
                    "description": f"🔍 يفحص: **`{s['current']}`**",
                    "color": color,
                    "fields": [
                        {"name": "📊 فحص", "value": f"`{s['checked']}`", "inline": True},
                        {"name": "🎯 صيد", "value": f"`{s['found']}`", "inline": True}
                    ],
                    "footer": {"text": "نسخة العودة للأصل | V21"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            if s["msg_id"] is None:
                r = requests.post(webhook + "?wait=true", json=payload)
                stats[platform]["msg_id"] = r.json()['id']
            else:
                requests.patch(f"{webhook}/messages/{s['msg_id']}", json=payload)
        except: pass
        time.sleep(5)

def send_hit(webhook, platform, user, color):
    requests.post(webhook, json={
        "content": "@everyone",
        "embeds": [{
            "title": f"🎯 صيد {platform} متاح!",
            "description": f"✅ اليوزر: **`{user}`**",
            "color": color
        }]
    })

def dc_worker(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            u = "".join(random.choices(chars, k=4))
            stats["discord"]["current"] = u
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": u}, headers=HEADERS, timeout=5)
            stats["discord"]["checked"] += 1
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["discord"]["found"] += 1
                send_hit(webhook, "Discord", u, 0x5865F2)
            time.sleep(0.7)
        except: time.sleep(2)

def ig_worker(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    while True:
        try:
            u = "".join(random.choices(chars, k=5))
            stats["instagram"]["current"] = u
            r = requests.get(f"https://www.instagram.com/{u}/?__a=1&__d=dis", headers=HEADERS, timeout=5)
            stats["instagram"]["checked"] += 1
            if r.status_code == 404:
                stats["instagram"]["found"] += 1
                send_hit(webhook, "Instagram", u, 0xE1306C)
            time.sleep(10)
        except: time.sleep(5)

def tw_worker(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            u = "".join(random.choices(chars, k=5))
            stats["twitter"]["current"] = u
            r = requests.get(f"https://twitter.com/{u}", headers=HEADERS, timeout=5)
            stats["twitter"]["checked"] += 1
            if r.status_code == 404:
                stats["twitter"]["found"] += 1
                send_hit(webhook, "Twitter", u, 0x1DA1F2)
            time.sleep(10)
        except: time.sleep(5)

if __name__ == "__main__":
    url = os.getenv('WEBHOOK_URL')
    if url:
        # تشغيل الإيمبدات
        threading.Thread(target=update_ui, args=(url, "discord", 0x5865F2, "https://cdn-icons-png.flaticon.com/512/2111/2111370.png"), daemon=True).start()
        threading.Thread(target=update_ui, args=(url, "instagram", 0xE1306C, "https://cdn-icons-png.flaticon.com/512/174/174855.png"), daemon=True).start()
        threading.Thread(target=update_ui, args=(url, "twitter", 0x1DA1F2, "https://cdn-icons-png.flaticon.com/512/733/733579.png"), daemon=True).start()
        
        # تشغيل الفحص
        threading.Thread(target=dc_worker, args=(url,), daemon=True).start()
        threading.Thread(target=ig_worker, args=(url,), daemon=True).start()
        threading.Thread(target=tw_worker, args=(url,), daemon=True).start()
        
        app.run(host='0.0.0.0', port=10000)
