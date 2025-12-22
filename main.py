import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"checked": 0, "found": 0, "current_user": "جاري البدء..."}

@app.route('/')
def home(): return "RADAR_STABLE_V14"

# إعدادات الانتحال (iOS 17)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

def update_radar_display(webhook):
    # هذه الدالة لتحديث رسالة العداد واليوزر الحالي في القناة
    msg_id = None
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار القنص المباشر (تحديث فوري)",
                    "description": f"🔍 جاري فحص الآن: **`{stats['current_user']}`**",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "📊 تم فحص", "value": f"`{stats['checked']}` يوزر", "inline": True},
                        {"name": "🎯 تم صيد", "value": f"`{stats['found']}` يوزر", "inline": True}
                    ],
                    "footer": {"text": "النظام يعمل بمحاكاة iPhone 15 Pro"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            if msg_id is None:
                r = requests.post(webhook + "?wait=true", json=payload)
                msg_id = r.json()['id']
            else:
                requests.patch(f"{webhook}/messages/{msg_id}", json=payload)
        except: pass
        time.sleep(3) # تحديث سريع جداً كل 3 ثواني عشان تشوف الحركة

def send_found(webhook, platform, user):
    config = {
        "discord": {"color": 0x5865F2, "icon": "https://cdn-icons-png.flaticon.com/512/2111/2111370.png"},
        "instagram": {"color": 0xE1306C, "icon": "https://cdn-icons-png.flaticon.com/512/174/174855.png"},
        "twitter": {"color": 0x1DA1F2, "icon": "https://cdn-icons-png.flaticon.com/512/733/733579.png"}
    }
    cfg = config[platform]
    payload = {
        "content": "@everyone",
        "embeds": [{
            "title": f"🎯 مبروك! صيد {platform} جديد",
            "description": f"✅ اليوزر: **`{user}`** متاح الآن!",
            "color": cfg["color"],
            "thumbnail": {"url": cfg["icon"]}
        }]
    }
    requests.post(webhook, json=payload)

def sniper_logic(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    social_chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    
    while True:
        # ديسكورد (4 خانات)
        u_dc = "".join(random.choices(chars, k=4))
        stats["current_user"] = u_dc + " (Discord)"
        try:
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", json={"username": u_dc}, headers=HEADERS, timeout=5)
            stats["checked"] += 1
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["found"] += 1
                send_found(webhook, "discord", u_dc)
        except: pass

        # انستقرام (5 خانات)
        u_ig = "".join(random.choices(social_chars, k=5))
        stats["current_user"] = u_ig + " (Instagram)"
        try:
            r = requests.get(f"https://www.instagram.com/{u_ig}/?__a=1&__d=dis", headers=HEADERS, timeout=5)
            stats["checked"] += 1
            if r.status_code == 404:
                stats["found"] += 1
                send_found(webhook, "instagram", u_ig)
        except: pass

        # تويتر (5 خانات)
        u_tw = "".join(random.choices(chars, k=5))
        stats["current_user"] = u_tw + " (Twitter)"
        try:
            r = requests.get(f"https://twitter.com/{u_tw}", headers=HEADERS, timeout=5)
            stats["checked"] += 1
            if r.status_code == 404:
                stats["found"] += 1
                send_found(webhook, "twitter", u_tw)
        except: pass

        time.sleep(2) # سرعة عالية للحركة

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if webhook:
        threading.Thread(target=update_radar_display, args=(webhook,), daemon=True).start()
        threading.Thread(target=sniper_logic, args=(webhook,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
