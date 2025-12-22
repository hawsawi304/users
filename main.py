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
def home(): return "DIAGNOSTIC_MODE_ACTIVE"

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
    except Exception as e:
        print(f"⚠️ خطأ في تحديث الإيمبد ({platform}): {e}")

def startup_test(webhook):
    """ فحص تشخيصي شامل عند البداية """
    test_user = "check_" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=12))
    print(f"🚀 بدأت عملية التشخيص... جاري فحص يوزر وهمي: {test_user}")
    try:
        # فحص جودة الاتصال
        r = requests.get(f"https://www.instagram.com/{test_user}", timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        print(f"📡 حالة اتصال الإنترنت (Instagram): {r.status_code}")
        
        if r.status_code == 404:
            print("✅ نظام 404 يعمل: اليوزر متاح فعلاً.")
            # فحص الويب هوك
            res = requests.post(webhook, json={"content": f"⚙️ **تقرير التشخيص:** الاتصال سليم، الويب هوك يعمل، واليوزر التجريبي متاح: `{test_user}`"})
            if res.status_code in [200, 204]:
                print("✅ الويب هوك سليم: الرسالة وصلت ديسكورد.")
            else:
                print(f"❌ مشكلة في الويب هوك! الكود المستلم: {res.status_code} - الرد: {res.text}")
    except Exception as e:
        print(f"❌ فشل التشخيص بالكامل! السبب: {e}")

def discord_worker(webhook):
    token = os.getenv('DISCORD_TOKEN')
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
        try:
            r = requests.get(f"https://discord.com/api/v9/users/{user}/profile", timeout=5)
            with lock: stats["discord"]["checked"] += 1; stats["discord"]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"@everyone 🎯 **ديسكورد متاح:** `{user}`"})
                with lock: stats["discord"]["found"] += 1
            update_embed(webhook, "discord")
        except: pass
        time.sleep(15)

def social_worker(platform, webhook):
    while True:
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
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
    if not webhook:
        print("❌ خطأ: لم يتم العثور على رابط WEBHOOK_URL في الإعدادات!")
    else:
        threading.Thread(target=startup_test, args=(webhook,)).start()
        threading.Thread(target=discord_worker, args=(webhook,), daemon=True).start()
        threading.Thread(target=social_worker, args=("instagram", webhook), daemon=True).start()
        threading.Thread(target=social_worker, args=("twitter", webhook), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
