import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"dc_c": 0, "dc_f": 0, "ig_c": 0, "ig_f": 0, "tw_c": 0, "tw_f": 0}

@app.route('/')
def home(): return "DIRECT_SNIPER_ACTIVE"

# هيدرز بسيطة ومباشرة (نفس اللي صادت لك أول مرة)
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def send_alert(webhook, platform, user):
    # إرسال منشن مباشر وقوي بدون تعقيد
    payload = {
        "content": f"@everyone 🎯 **صيد {platform} جديد!** \n✅ اليوزر: **`{user}`**",
        "username": "Sniper Bot"
    }
    requests.post(webhook, json=payload)

def update_ui(webhook):
    # تحديث العداد كل 10 ثواني (عشان ما يزحم القناة)
    m_id = {"dc": None, "ig": None, "tw": None}
    while True:
        try:
            for p, color in [("dc", 0x5865F2), ("ig", 0xE1306C), ("tw", 0x1DA1F2)]:
                payload = {
                    "embeds": [{
                        "title": f"📡 رادار {p.upper()}",
                        "description": f"📊 فحص: `{stats[p+'_c']}` | 🎯 صيد: `{stats[p+'_f']}`",
                        "color": color
                    }]
                }
                if m_id[p] is None:
                    r = requests.post(webhook + "?wait=true", json=payload)
                    m_id[p] = r.json()['id']
                else:
                    requests.patch(f"{webhook}/messages/{m_id[p]}", json=payload)
            time.sleep(10)
        except: pass

def dc_engine(webhook):
    while True:
        try:
            u = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": u}, headers=H, timeout=5)
            stats["dc_c"] += 1
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["dc_f"] += 1
                send_alert(webhook, "Discord", u) # منشن فوري
            time.sleep(0.8) 
        except: time.sleep(2)

def social_engine(webhook):
    while True:
        try:
            # انستا
            u_ig = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
            r_ig = requests.get(f"https://www.instagram.com/{u_ig}/?__a=1&__d=dis", headers=H, timeout=5)
            stats["ig_c"] += 1
            if r_ig.status_code == 404:
                stats["ig_f"] += 1
                send_alert(webhook, "Instagram", u_ig)
            
            # تويتر
            u_tw = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5))
            r_tw = requests.get(f"https://twitter.com/{u_tw}", headers=H, timeout=5)
            stats["tw_c"] += 1
            if r_tw.status_code == 404:
                stats["tw_f"] += 1
                send_alert(webhook, "Twitter", u_tw)
            time.sleep(10)
        except: time.sleep(5)

if __name__ == "__main__":
    url = os.getenv('WEBHOOK_URL')
    if url:
        threading.Thread(target=update_ui, args=(url,), daemon=True).start()
        threading.Thread(target=dc_engine, args=(url,), daemon=True).start()
        threading.Thread(target=social_engine, args=(url,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
