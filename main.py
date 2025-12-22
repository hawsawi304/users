import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"checked": 0, "found": 0, "last_check": "لا يوجد"}

@app.route('/')
def home(): return "SYSTEM_ACTIVE_V11"

def send_update(webhook):
    global stats
    while True:
        # يرسل تحديث للقناة كل 20 دقيقة عشان يطمنك إنه شغال
        payload = {
            "embeds": [{
                "title": "📡 رادار الصيد يعمل الآن",
                "color": 0x2ecc71,
                "fields": [
                    {"name": "📊 تم فحص", "value": f"`{stats['checked']}` يوزر", "inline": True},
                    {"name": "🎯 تم صيد", "value": f"`{stats['found']}` يوزر", "inline": True},
                    {"name": "🕒 آخر فحص", "value": f"`{stats['last_check']}`", "inline": False}
                ],
                "footer": {"text": "تحديث تلقائي كل 20 دقيقة"}
            }]
        }
        try: requests.post(webhook, json=payload)
        except: pass
        time.sleep(1200) # عشان ما يزعجك ويزحم القناة

def check_all(user, platform, webhook):
    global stats
    stats["checked"] += 1
    stats["last_check"] = user
    
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X)"}
    
    try:
        if platform == "discord":
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": user}, headers=headers, timeout=5)
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["found"] += 1
                requests.post(webhook, json={"content": f"@everyone 🎯 **ديسكورد متاح:** `{user}`"})
        
        elif platform == "instagram":
            r = requests.get(f"https://www.instagram.com/{user}/?__a=1&__d=dis", headers=headers, timeout=5)
            if r.status_code == 404:
                stats["found"] += 1
                requests.post(webhook, json={"content": f"@everyone 📸 **انستا متاح:** `{user}`"})
    except: pass

def sniper_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        # ديسكورد (4)
        target_dc = "".join(random.choices(chars, k=4))
        check_all(target_dc, "discord", webhook)
        
        # انستا (5)
        target_ig = "".join(random.choices(chars + "._", k=5))
        check_all(target_ig, "instagram", webhook)
        
        time.sleep(15)

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if webhook:
        # تشغيل نظام التحديثات في خيط منفصل
        threading.Thread(target=send_update, args=(webhook,), daemon=True).start()
        # تشغيل القناص
        threading.Thread(target=sniper_engine, args=(webhook,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
