import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"checked": 0, "found": 0, "current_user": "جاري البدء..."}

@app.route('/')
def home(): return "ONE_EMBED_SYSTEM_ACTIVE"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

def monitor_system(webhook):
    # هذه الدالة هي اللي تمسك إيمبد واحد وتحدثه (تغير اليوزر والعداد)
    msg_id = None
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار الفحص المباشر",
                    "description": f"🔍 يفحص الآن: **`{stats['current_user']}`**",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "📊 المجموع", "value": f"`{stats['checked']}`", "inline": True},
                        {"name": "🎯 الصيد", "value": f"`{stats['found']}`", "inline": True}
                    ],
                    "footer": {"text": "يتحدث تلقائياً | محاكاة iOS 17"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            if msg_id is None:
                # أول مرة يرسل الرسالة ويحفظ رقمها (ID)
                r = requests.post(webhook + "?wait=true", json=payload)
                msg_id = r.json()['id']
            else:
                # المرات اللي بعدها يسوي تعديل (Edit) لنفس الرسالة
                requests.patch(f"{webhook}/messages/{msg_id}", json=payload)
        except: pass
        time.sleep(2) # تحديث سريع جداً لليوزر والعداد

def send_found(webhook, platform, user):
    # إذا لقى صيدة يرسل إيمبد منفصل (بشعاره) مع منشن
    config = {
        "discord": {"color": 0x5865F2, "icon": "https://cdn-icons-png.flaticon.com/512/2111/2111370.png"},
        "instagram": {"color": 0xE1306C, "icon": "https://cdn-icons-png.flaticon.com/512/174/174855.png"},
        "twitter": {"color": 0x1DA1F2, "icon": "https://cdn-icons-png.flaticon.com/512/733/733579.png"}
    }
    cfg = config.get(platform)
    payload = {
        "content": "@everyone",
        "embeds": [{
            "title": f"🎯 مبروك! صيد {platform} جديد",
            "thumbnail": {"url": cfg["icon"]},
            "description": f"✅ اليوزر: **`{user}`** متاح!",
            "color": cfg["color"]
        }]
    }
    requests.post(webhook, json=payload)

def sniper_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            # فحص ديسكورد (4)
            u_dc = "".join(random.choices(chars, k=4))
            stats["current_user"] = u_dc + " (DC)"
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", json={"username": u_dc}, headers=HEADERS, timeout=5)
            stats["checked"] += 1
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["found"] += 1
                send_found(webhook, "discord", u_dc)

            # فحص انستا (5)
            u_ig = "".join(random.choices(chars + "._", k=5))
            stats["current_user"] = u_ig + " (IG)"
            r_ig = requests.get(f"https://www.instagram.com/{u_ig}/?__a=1&__d=dis", headers=HEADERS, timeout=5)
            stats["checked"] += 1
            if r_ig.status_code == 404:
                stats["found"] += 1
                send_found(webhook, "instagram", u_ig)

        except: pass
        time.sleep(1) # سرعة الفحص

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if webhook:
        threading.Thread(target=monitor_system, args=(webhook,), daemon=True).start()
        threading.Thread(target=sniper_engine, args=(webhook,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
