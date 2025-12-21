import os, random, time, requests, threading
from flask import Flask
from datetime import datetime

app = Flask('')
# إحصائيات دقيقة جداً
stats = {
    "discord": {"checked": 0, "found": 0, "last": "Starting...", "msg_id": None, "color": 0x5865F2},
    "instagram": {"checked": 0, "found": 0, "last": "Starting...", "msg_id": None, "color": 0xE1306C},
    "twitter": {"checked": 0, "found": 0, "last": "Starting...", "msg_id": None, "color": 0x1DA1F2}
}

lock = threading.Lock()

@app.route('/')
def home(): return "TURBO_SNIPER_v2025_ONLINE"

def update_live_embed(webhook_url, platform):
    with lock:
        data = stats[platform]
        payload = {
            "embeds": [{
                "title": f"🚀 رادار {platform.upper()} المطور",
                "description": (
                    f"📊 **الإحصائيات الحالية:**\n"
                    f"┣ المفحوص: `{data['checked']}`\n"
                    f"┗ الصيد: `{data['found']}`\n\n"
                    f"🔍 **آخر فحص:** `{data['last']}`\n"
                    f"⚡ **الحالة:** `فحص نشط (تيربو)`"
                ),
                "color": data["color"],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "تحديث لحظي - الإصدار الأخير 2025"}
            }]
        }
    
    try:
        if data["msg_id"] is None:
            r = requests.post(f"{webhook_url}?wait=true", json=payload)
            if r.status_code in [200, 201]: data["msg_id"] = r.json()['id']
        else:
            requests.patch(f"{webhook_url}/messages/{data['msg_id']}", json=payload)
    except: pass

def discord_worker(token, webhook):
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
        try:
            r = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={user}', 
                             headers={'Authorization': token}, timeout=5)
            with lock:
                stats["discord"]["checked"] += 1
                stats["discord"]["last"] = user
            if r.status_code == 200 and r.json().get('is_unique'):
                requests.post(webhook, json={"content": f"@everyone 🎯 **ديسكورد رباعي لقطة!** `{user}`"})
                with lock: stats["discord"]["found"] += 1
            update_live_embed(webhook, "discord")
        except: pass
        time.sleep(15) # سرعة عالية جداً لديسكورد

def social_worker(platform, webhook):
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
        url = f"https://www.{platform}.com/{user}"
        try:
            r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            with lock:
                stats[platform]["checked"] += 1
                stats[platform]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"📸 **{platform} متاح:** `{user}`"})
                with lock: stats[platform]["found"] += 1
            update_live_embed(webhook, platform)
        except: pass
        time.sleep(10) # سرعة جنونية للسوشيال

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    webhook = os.getenv('WEBHOOK_URL')
    
    # تشغيل المسارات المتوازية
    threading.Thread(target=discord_worker, args=(token, webhook), daemon=True).start()
    threading.Thread(target=social_worker, args=("instagram", webhook), daemon=True).start()
    threading.Thread(target=social_worker, args=("twitter", webhook), daemon=True).start()
    
    app.run(host='0.0.0.0', port=10000)
