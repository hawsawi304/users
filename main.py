import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {
    "discord": {"checked": 0, "found": 0, "last": "N/A"},
    "instagram": {"checked": 0, "found": 0, "last": "N/A"},
    "twitter": {"checked": 0, "found": 0, "last": "N/A"},
    "msg_id": None
}
lock = threading.Lock()

def update_monitor(webhook_url):
    with lock:
        now = datetime.datetime.now().strftime('%H:%M:%S')
        payload = {
            "embeds": [{
                "title": "⚡ رادار الصيد الشامل (4-5 خانات)",
                "description": (
                    f"🔹 **ديسكورد:** مفحوص `{stats['discord']['checked']}` | صيد `{stats['discord']['found']}`\n"
                    f"🔸 **انستقرام:** مفحوص `{stats['instagram']['checked']}` | صيد `{stats['instagram']['found']}`\n"
                    f"🔹 **تويتر:** مفحوص `{stats['twitter']['checked']}` | صيد `{stats['twitter']['found']}`\n\n"
                    f"⏱️ **آخر تحديث:** `{now}`"
                ),
                "color": 0x00ff00,
                "footer": {"text": "النظام يعمل بنظام فحص الوجود (404 Detection)"}
            }]
        }
    try:
        if stats["msg_id"]: requests.patch(f"{webhook_url}/messages/{stats['msg_id']}", json=payload)
        else:
            r = requests.post(f"{webhook_url}?wait=true", json=payload)
            if r.status_code in [200, 201]: stats["msg_id"] = r.json()['id']
    except: pass

def check_discord(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        user = "".join(random.choices(chars, k=4))
        try:
            # فحص الوجود (الطريقة المضمونة)
            r = requests.get(f"https://discord.com/api/v9/users/{user}/profile", timeout=5)
            with lock: stats["discord"]["checked"] += 1; stats["discord"]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"@everyone 🎯 **صيد ديسكورد رباعي:** `{user}`"})
                with lock: stats["discord"]["found"] += 1
        except: pass
        time.sleep(10)

def check_social(platform, webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    while True:
        user = "".join(random.choices(chars, k=5))
        url = f"https://www.{platform}.com/{user}"
        try:
            r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            with lock: stats[platform]["checked"] += 1; stats[platform]["last"] = user
            if r.status_code == 404:
                requests.post(webhook, json={"content": f"📸 **صيد {platform} خماسي:** `{user}`"})
                with lock: stats[platform]["found"] += 1
        except: pass
        time.sleep(8)

def monitor_thread(webhook):
    while True:
        update_monitor(webhook)
        time.sleep(30)

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    threading.Thread(target=check_discord, args=(webhook,), daemon=True).start()
    threading.Thread(target=check_social, args=("instagram", webhook), daemon=True).start()
    threading.Thread(target=check_social, args=("twitter", webhook), daemon=True).start()
    threading.Thread(target=monitor_thread, args=(webhook,), daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
