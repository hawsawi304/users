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
def home(): return "FINAL_STABLE_v5"

def update_embed(webhook_url, platform):
    with lock:
        data = stats[platform]
        now = datetime.datetime.now().strftime('%H:%M:%S')
        payload = {
            "embeds": [{
                "title": f"🛰️ رادار {platform.upper()}",
                "description": f"📊 **الفحص:** `{data['checked']}`\n🎯 **المتاح:** `{data['found']}`\n🔍 **آخر يوزر:** `{data['last']}`\n⏱️ **تحديث:** `{now}`",
                "color": data["color"]
            }]
        }
    try:
        if data["msg_id"] is None:
            r = requests.post(f"{webhook_url}?wait=true", json=payload)
            if r.status_code in [200, 201]: data["msg_id"] = r.json()['id']
        else:
            requests.patch(f"{webhook_url}/messages/{data['msg_id']}", json=payload)
    except: pass

def initial_ping(webhook):
    """ إرسال إشارة فورية للديسكورد أول ما يشتغل البوت """
    print("📡 جاري إرسال إشارة البدء للديسكورد...")
    try:
        res = requests.post(webhook, json={
            "content": "🚀 **النظام اشتغل!**\nإذا وصلتكم هذي الرسالة يعني الويب هوك سليم والبوت بدأ يجلد يوزرات الآن."
        })
        print(f"📡 نتيجة إرسال الإشارة: {res.status_code}")
    except Exception as e:
        print(f"❌ فشل إرسال الإشارة: {e}")

def discord_worker(webhook):
    token = os.getenv('DISCORD_TOKEN')
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
        try:
            # استخدام رابط أبسط للفحص لتجنب التعليق
            r = requests.get(f"https://discordapp.com/api/v9/users/{user}/profile", timeout=10)
            with lock:
                stats["discord"]["checked"] += 1
                stats["discord"]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"@everyone 🎯 **صيد ديسكورد:** `{user}`"})
                with lock: stats["discord"]["found"] += 1
            update_embed(webhook, "discord")
        except: pass
        time.sleep(12)

def social_worker(platform, webhook):
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
        try:
            r = requests.get(f"https://www.{platform}.com/{user}", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            with lock:
                stats[platform]["checked"] += 1
                stats[platform]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"📸 **صيد {platform}:** `{user}`"})
                with lock: stats[platform]["found"] += 1
            update_embed(webhook, platform)
        except: pass
        time.sleep(10)

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if not webhook:
        print("❌ خطأ: WEBHOOK_URL مفقود!")
    else:
        # أرسل الإشارة فوراً في المسار الرئيسي قبل الـ Threads
        initial_ping(webhook)
        
        threading.Thread(target=discord_worker, args=(webhook,), daemon=True).start()
        threading.Thread(target=social_worker, args=("instagram", webhook), daemon=True).start()
        threading.Thread(target=social_worker, args=("twitter", webhook), daemon=True).start()
        
        app.run(host='0.0.0.0', port=10000)
