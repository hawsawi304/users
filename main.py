import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "RUNNING_STABLE"

def send_embed(webhook, platform, user):
    colors = {"discord": 0x5865F2, "instagram": 0xE1306C, "twitter": 0x1DA1F2}
    payload = {
        "content": "@everyone",
        "embeds": [{
            "title": "🎯 صيد متاح جديد!",
            "description": f"✅ اليوزر: **`{user}`**\n🌐 المنصة: **{platform}**",
            "color": colors.get(platform, 0x000000),
            "footer": {"text": "Elite Sniper V12"},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    requests.post(webhook, json=payload)

def sniper():
    webhook = os.getenv('WEBHOOK_URL')
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    social_chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    
    # إشارة بدء في القناة
    requests.post(webhook, json={"content": "🚀 **بدأت عملية القنص (نسخة الاستقرار V12)**\n- ديسكورد: 4 خانات\n- انستا وتويتر: 5 خانات"})

    while True:
        try:
            # 1. ديسكورد (4 خانات فقط)
            target_dc = "".join(random.choices(chars, k=4))
            r_dc = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                                json={"username": target_dc}, timeout=5)
            if r_dc.status_code == 200 and r_dc.json().get("taken") == False:
                send_embed(webhook, "discord", target_dc)

            # 2. انستقرام (5 خانات)
            target_ig = "".join(random.choices(social_chars, k=5))
            r_ig = requests.get(f"https://www.instagram.com/{target_ig}/?__a=1&__d=dis", timeout=5)
            if r_ig.status_code == 404:
                send_embed(webhook, "instagram", target_ig)

            # 3. تويتر (5 خانات)
            target_tw = "".join(random.choices(chars, k=5))
            r_tw = requests.get(f"https://twitter.com/{target_tw}", timeout=5)
            if r_tw.status_code == 404:
                send_embed(webhook, "twitter", target_tw)

            # طبعة في اللوق عشان تتطمن إنه شغال
            print(f"📡 Checked: {target_dc} | {target_ig} | {target_tw}")
            
        except:
            pass
        
        time.sleep(12) # سرعة الفحص (12 ثانية)

if __name__ == "__main__":
    threading.Thread(target=sniper, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
