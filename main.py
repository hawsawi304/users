import requests
import time
import os
import random
import string
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Sniper is Active"

# --- المتغيرات ---
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MY_ID = os.getenv("YOUR_USER_ID")

# --- دالة الصيد ---
def start_sniping():
    # تأخير بسيط للتأكد أن السيرفر استقر
    time.sleep(15)
    print("🚀 الصيد بدأ الآن...")

    # إرسال رسالة ترحيبية للتأكد أن الويب هوك شغال
    initial_payload = {"content": "✅ تم تشغيل الصياد بنجاح وهو الآن يراقب..."}
    try:
        requests.post(WEBHOOK_URL, json=initial_payload)
    except Exception as e:
        print("Webhook error:", e)

    while True:
        # توليد يوزر 4 أزرار
        target = ''.join(random.choice(string.ascii_lowercase) for _ in range(3)) + random.choice("._0123456789")
        headers = {"Authorization": TOKEN}
        url = f"https://discord.com/api/v9/users/search?query={target}"

        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                users = res.json().get('users', [])
                if not any(u.get('username', '').lower() == target.lower() for u in users):
                    msg = {
                        "content": f"<@{MY_ID}> 🎯 صيد محتمل: `{target}`",
                        "username": "Ultra Sniper"
                    }
                    requests.post(WEBHOOK_URL, json=msg)
                    print(f"Hit: {target}")
            elif res.status_code == 429:
                time.sleep(60)
            elif res.status_code == 401:
                print("❌ التوكن خطأ!")
                break
        except Exception as e:
            print("Request error:", e)

        # وقت أمان (25 ثانية)
        time.sleep(25)

# --- التشغيل الرئيسي ---
if __name__ == "__main__":
    # تشغيل الصيد في الخلفية
    daemon = Thread(target=start_sniping, daemon=True)
    daemon.start()
    
    # تشغيل Flask
    app.run(host='0.0.0.0', port=10000)
