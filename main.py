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
def home(): return "SYSTEM_STABLE_v4"

def update_embed(webhook_url, platform):
    with lock:
        data = stats[platform]
        now = datetime.datetime.now().strftime('%H:%M:%S')
        payload = {
            "embeds": [{
                "title": f"🛰️ رادار {platform.upper()}",
                "description": (
                    f"📊 **الفحص:** `{data['checked']}`\n"
                    f"🎯 **المتاح:** `{data['found']}`\n"
                    f"🔍 **آخر يوزر:** `{data['last']}`\n"
                    f"⏱️ **آخر تحديث:** `{now}`"
                ),
                "color": data["color"],
                "footer": {"text": "النظام يعمل بنظام فحص الوجود"}
            }]
        }
    try:
        if data["msg_id"] is None:
            r = requests.post(f"{webhook_url}?wait=true", json=payload)
            if r.status_code in [200, 201]: data["msg_id"] = r.json()['id']
        else:
            requests.patch(f"{webhook_url}/messages/{data['msg_id']}", json=payload)
    except: pass

def startup_test(webhook):
    """ فحص تأكيدي لمرة واحدة عند التشغيل """
    test_user = "test_user_" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=10))
    print(f"Checking test user: {test_user}")
    try:
        r = requests.get(f"https://www.instagram.com/{test_user}", timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 404:
            requests.post(webhook, json={"content": f"✅ **تم الاتصال بنجاح!**\n فحص التأكيد صاد يوزر متاح: `{test_user}`\nالآن بدأ الصيد الفعلي..."})
    except: pass

def discord_worker(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        user = "".join(random.choices(chars, k=4))
        try:
            r = requests.get(f"https://discord.com/api/v9/users/{user}/profile", timeout=5)
            with lock: stats["discord"]["checked"] += 1; stats["discord"]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"@everyone 🎯 **صيد ديسكورد رباعي:** `{user}`"})
                with lock: stats["discord"]["found"] += 1
            update_embed(webhook, "discord")
        except: pass
        time.sleep(15)

def social_worker(platform, webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    while True:
        user = "".join(random.choices(chars, k=5))
        try:
            r = requests.get(f"https://www.{platform}.com/{user}", timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            with lock: stats[platform]["checked"] += 1; stats[platform]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"📸 **{platform.capitalize()} متاح:** `{user}`"})
                with lock: stats[platform]["found"] += 1
            update_embed(webhook, platform)
        except: pass
        time.sleep(12)

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    
    # 1. تشغيل فحص التأكيد أولاً
    threading.Thread(target=startup_test, args=(webhook,)).start()
    
    # 2. تشغيل الفحص المستمر
    threading.Thread(target=discord_worker, args=(webhook,), daemon=True).start()
    threading.Thread(target=social_worker, args=("instagram", webhook), daemon=True).start()
    threading.Thread(target=social_worker, args=("twitter", webhook), daemon=True).start()
    
    app.run(host='0.0.0.0', port=10000)
