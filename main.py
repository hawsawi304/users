import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"checked": 0, "found": 0, "current": "...", "msg_id": None}

@app.route('/')
def home(): 
    return f"SNIPER_V7_STATUS: {stats['checked']} CHECKED"

def update_status(webhook):
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار V7 المطور - حالة التشغيل",
                    "description": f"🔍 يفحص الآن: `{stats['current']}`",
                    "color": 0x2ecc71,
                    "fields": [
                        {"name": "📊 الفحوصات", "value": f"`{stats['checked']}`", "inline": True},
                        {"name": "🎯 المصيدة", "value": f"`{stats['found']}`", "inline": True}
                    ],
                    "footer": {"text": "تحديث مباشر | 2025 Mode"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            if stats["msg_id"] is None:
                r = requests.post(webhook + "?wait=true", json=payload)
                if r.status_code == 200:
                    stats["msg_id"] = r.json()['id']
                    print("✅ تم إرسال الإيمبد الأول بنجاح")
                else:
                    print(f"❌ خطأ في الويب هوك: {r.status_code}")
            else:
                requests.patch(f"{webhook}/messages/{stats['msg_id']}", json=payload)
        except Exception as e:
            print(f"⚠️ خطأ في التحديث: {e}")
        time.sleep(10)

def sniper():
    webhook = os.getenv('WEBHOOK_URL')
    if not webhook:
        print("🛑 خطأ كارثي: لم يتم العثور على WEBHOOK_URL في الإعدادات (Env)!")
        return

    # رسالة ترحيب نصية للتأكد من وصول التنبيهات
    requests.post(webhook, json={"content": "🚀 **تم تشغيل القناص بنجاح (نسخة 22/12 المحدثة)**"})
    
    threading.Thread(target=update_status, args=(webhook,), daemon=True).start()

    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            user = "".join(random.choices(chars, k=4)) # رباعي ديسكورد
            stats["current"] = user
            
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                               json={"username": user}, timeout=5)
            stats["checked"] += 1
            
            if r.status_code == 200 and r.json().get("taken") == False:
                stats["found"] += 1
                requests.post(webhook, json={"content": f"🎯 **صيد جديد:** `{user}` @everyone"})
            
            time.sleep(1.5) # سرعة عالية وآمنة
        except:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=sniper, daemon=True).start()
    # تشغيل على بورت 10000 كما هو مطلوب في Render
    app.run(host='0.0.0.0', port=10000)
