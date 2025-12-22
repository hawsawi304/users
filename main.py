import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {
    "discord": {"checked": 0, "found": 0, "current": "...", "msg_id": None},
    "instagram": {"checked": 0, "found": 0, "current": "...", "msg_id": None},
    "twitter": {"checked": 0, "found": 0, "current": "...", "msg_id": None}
}

@app.route('/')
def home(): return "SYSTEM_V19_READY"

# هيدرز آيفون 15 برو لكسر حماية المواقع
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9"
}

def update_embed(webhook, platform, color, icon):
    while True:
        try:
            s = stats[platform]
            payload = {
                "embeds": [{
                    "title": f"🛡️ رادار {platform.upper()} المطور",
                    "thumbnail": {"url": icon},
                    "description": f"🔍 يبحث الآن عن: **`{s['current']}`**",
                    "color": color,
                    "fields": [
                        {"name": "📊 الفحوصات", "value": f"`{s['checked']}`", "inline": True},
                        {"name": "🎯 المصيدة", "value": f"`{s['found']}`", "inline": True}
                    ],
                    "footer": {"text": "Elite Sniper V19 | iOS Mode"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            if s["msg_id"] is None:
                r = requests.post(webhook + "?wait=true", json=payload)
                stats[platform]["msg_id"] = r.json()['id']
            else:
                requests.patch(f"{webhook}/messages/{s['msg_id']}", json=payload)
        except: pass
        time.sleep(6) # تحديث الإيمبدات بشكل متناوب

def send_alert(webhook, platform, user, color):
    payload = {
        "content": f"@everyone 🎯 **تم صيد يوزر {platform} متاح!**",
        "embeds": [{
            "title": "✅ صيد جديد جاهز للتسجيل",
            "description": f"اليوزر: **`{user}`**",
            "color": color,
            "footer": {"text": "تنبيه الصيد الفوري"}
        }]
    }
    requests.post(webhook, json=payload)

def dc_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            u = "".join(random.choices(chars, k=4)) # رباعي ديسكورد
            stats["discord"]["current"] = u
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": u}, headers=HEADERS, timeout=5)
            stats["discord"]["checked"] += 1
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["discord"]["found"] += 1
                send_alert(webhook, "Discord", u, 0x5865F2)
            time.sleep(0.5) # سرعة عالية جداً لديسكورد
        except: time.sleep(2)

def ig_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    while True:
        try:
            u = "".join(random.choices(chars, k=5)) # خماسي انستا
            stats["instagram"]["current"] = u
            r = requests.get(f"https://www.instagram.com/{u}/?__a=1&__d=dis", headers=HEADERS, timeout=5)
            stats["instagram"]["checked"] += 1
            if r.status_code == 404:
                stats["instagram"]["found"] += 1
                send_alert(webhook, "Instagram", u, 0xE1306C)
            time.sleep(12) # وقت آمن لمنع حظر انستا
        except: time.sleep(5)

def tw_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            u = "".join(random.choices(chars, k=5)) # خماسي تويتر
            stats["twitter"]["current"] = u
            r = requests.get(f"https://twitter.com/{u}", headers=HEADERS, timeout=5)
            stats["twitter"]["checked"] += 1
            if r.status_code == 404:
                stats["twitter"]["found"] += 1
                send_alert(webhook, "Twitter", u, 0x1DA1F2)
            time.sleep(12) # وقت آمن لمنع حظر تويتر
        except: time.sleep(5)

if __name__ == "__main__":
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        # تشغيل شاشات العرض المنفصلة
        threading.Thread(target=update_embed, args=(webhook_url, "discord", 0x5865F2, "https://cdn-icons-png.flaticon.com/512/2111/2111370.png"), daemon=True).start()
        threading.Thread(target=update_embed, args=(webhook_url, "instagram", 0xE1306C, "https://cdn-icons-png.flaticon.com/512/174/174855.png"), daemon=True).start()
        threading.Thread(target=update_embed, args=(webhook_url, "twitter", 0x1DA1F2, "https://cdn-icons-png.flaticon.com/512/733/733579.png"), daemon=True).start()
        
        # تشغيل محركات الصيد
        threading.Thread(target=dc_engine, args=(webhook_url,), daemon=True).start()
        threading.Thread(target=ig_engine, args=(webhook_url,), daemon=True).start()
        threading.Thread(target=tw_engine, args=(webhook_url,), daemon=True).start()
        
        app.run(host='0.0.0.0', port=10000)
