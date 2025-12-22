import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"checked": 0, "found": 0, "current_user": "جاري البدء..."}

@app.route('/')
def home(): return "SYSTEM_STABLE_V16"

# قائمة هويات أجهزة مختلفة لتضليل المواقع
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def monitor_system(webhook):
    msg_id = None
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار القنص المطور (V16)",
                    "description": f"🔍 يفحص الآن: **`{stats['current_user']}`**",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "📊 تم فحص", "value": f"`{stats['checked']}`", "inline": True},
                        {"name": "🎯 تم صيد", "value": f"`{stats['found']}`", "inline": True}
                    ],
                    "footer": {"text": "نظام الحماية من الحظر مفعل ✅"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            if msg_id is None:
                r = requests.post(webhook + "?wait=true", json=payload)
                msg_id = r.json()['id']
            else:
                requests.patch(f"{webhook}/messages/{msg_id}", json=payload)
        except: pass
        time.sleep(5)

def send_found(webhook, platform, user):
    config = {
        "discord": {"color": 0x5865F2, "icon": "https://cdn-icons-png.flaticon.com/512/2111/2111370.png"},
        "instagram": {"color": 0xE1306C, "icon": "https://cdn-icons-png.flaticon.com/512/174/174855.png"},
        "twitter": {"color": 0x1DA1F2, "icon": "https://cdn-icons-png.flaticon.com/512/733/733579.png"}
    }
    cfg = config.get(platform)
    payload = {
        "content": "@everyone",
        "embeds": [{
            "title": f"🎯 مبروك! صيد {platform} نادِر",
            "thumbnail": {"url": cfg["icon"]},
            "description": f"✅ اليوزر: **`{user}`** متاح للتسجيل!",
            "color": cfg["color"]
        }]
    }
    requests.post(webhook, json=payload)

def sniper_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            head = {"User-Agent": random.choice(USER_AGENTS)}
            
            # 1. ديسكورد (4 خانات)
            u_dc = "".join(random.choices(chars, k=4))
            stats["current_user"] = u_dc + " (DC)"
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", json={"username": u_dc}, headers=head, timeout=5)
            stats["checked"] += 1
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["found"] += 1
                send_found(webhook, "discord", u_dc)

            # 2. انستقرام (5 خانات)
            u_ig = "".join(random.choices(chars + "._", k=5))
            stats["current_user"] = u_ig + " (IG)"
            r_ig = requests.get(f"https://www.instagram.com/{u_ig}/", headers=head, timeout=5)
            stats["checked"] += 1
            if r_ig.status_code == 404:
                stats["found"] += 1
                send_found(webhook, "instagram", u_ig)

            # 3. تويتر (5 خانات)
            u_tw = "".join(random.choices(chars, k=5))
            stats["current_user"] = u_tw + " (TW)"
            r_tw = requests.get(f"https://twitter.com/{u_tw}", headers=head, timeout=5)
            stats["checked"] += 1
            if r_tw.status_code == 404:
                stats["found"] += 1
                send_found(webhook, "twitter", u_tw)

        except: pass
        time.sleep(12) # توقيت "ذهبي" يمنع الحظر ويخلي الصيد مستمر

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if webhook:
        threading.Thread(target=monitor_system, args=(webhook,), daemon=True).start()
        threading.Thread(target=sniper_engine, args=(webhook,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
