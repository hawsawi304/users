import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {
    "discord": {"checked": 0, "found": 0, "last": "N/A", "msg_id": None, "color": 0x5865F2},
    "instagram": {"checked": 0, "found": 0, "last": "N/A", "msg_id": None, "color": 0xE1306C},
    "twitter": {"checked": 0, "found": 0, "last": "N/A", "msg_id": None, "color": 0x1DA1F2}
}
lock = threading.Lock()

@app.route('/')
def home(): return "SYSTEM_LIVE_2025"

def update_embed(webhook_url, platform):
    with lock:
        data = stats[platform]
        # استخدام التوقيت المحلي للسعودية أو توقيت السيرفر
        now = datetime.datetime.now().strftime('%H:%M:%S')
        payload = {
            "embeds": [{
                "title": f"🛰️ رادار {platform.upper()} - تحديث لحظي",
                "description": (
                    f"📊 **حالة الفحص:**\n"
                    f"┣ المفحوص: `{data['checked']}`\n"
                    f"┗ المرشحين للصيد: `{data['found']}`\n\n"
                    f"🔍 **آخر محاولة:** `{data['last']}`\n"
                    f"⏱️ **آخر تحديث:** `{now}`"
                ),
                "color": data["color"],
                "footer": {"text": "النظام يعمل بأقصى سرعة (Turbo Mode)"}
            }]
        }
    try:
        if data["msg_id"] is None:
            r = requests.post(f"{webhook_url}?wait=true", json=payload)
            if r.status_code in [200, 201]: data["msg_id"] = r.json()['id']
        else:
            requests.patch(f"{webhook_url}/messages/{data['msg_id']}", json=payload)
    except: pass

def discord_logic():
    token = os.getenv('DISCORD_TOKEN')
    webhook = os.getenv('WEBHOOK_URL')
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
        try:
            r = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={user}', headers={'Authorization': token}, timeout=5)
            with lock:
                stats["discord"]["checked"] += 1
                stats["discord"]["last"] = user
            
            # المنطق المرن: أي يوزر لا يعطي خطأ صريح نعتبره "مرشح"
            if r.status_code == 200:
                res = r.json()
                if res.get('is_unique') or not res.get('suggestions'):
                    requests.post(webhook, json={"content": f"@everyone ⚠️ **مرشح قوي ديسكورد:** `{user}` - جربه يدوي!"})
                    with lock: stats["discord"]["found"] += 1
            
            update_embed(webhook, "discord")
        except: pass
        time.sleep(20)

def social_logic(platform):
    webhook = os.getenv('WEBHOOK_URL')
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
        try:
            r = requests.get(f"https://www.{platform}.com/{user}", timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            with lock:
                stats[platform]["checked"] += 1
                stats[platform]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"📸 **مرشح {platform}:** `{user}`"})
                with lock: stats[platform]["found"] += 1
            update_embed(webhook, platform)
        except: pass
        time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=discord_logic, daemon=True).start()
    threading.Thread(target=social_logic, args=("instagram",), daemon=True).start()
    threading.Thread(target=social_logic, args=("twitter",), daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
