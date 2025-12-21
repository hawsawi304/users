import os, random, time, requests, threading
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "STABLE SNIPER v20.0"

def log_to_discord(webhook_url, content):
    try:
        requests.post(webhook_url, json={"content": content})
    except: pass

def sniper():
    token = os.getenv('DISCORD_TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')
    
    # استخدام Session لثبات الاتصال
    session = requests.Session()
    session.headers.update({'Authorization': token, 'Content-Type': 'application/json'})

    # --- اختبار فوري عند التشغيل ---
    test_name = f"test_check_{random.randint(1000, 9999)}"
    print(f"🔍 جاري اختبار التنبيهات بيوزر: {test_name}")
    log_to_discord(webhook_url, f"🚀 البوت اشتغل! جاري اختبار الصيد على: `{test_name}`")
    
    while True:
        # توليد يوزر رباعي صافي (حروف وأرقام فقط)
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
        
        try:
            url = f'https://discord.com/api/v9/users/@me/suffixes?username={user}'
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                res_data = response.json()
                # التحقق الشامل (أهم جزء)
                if res_data.get('is_unique') is True or res_data.get('available') is True:
                    # صيد مؤكد! منشن فوراً
                    alert = f"⚠️ @everyone **لقيت يوزر متاح!!**\n🎯 اليوزر: `{user}`\n💎 المنصة: ديسكورد"
                    log_to_discord(webhook_url, alert)
                    print(f"✅ SUCCESS: {user}")
                else:
                    print(f"❌ Taken: {user}")
            
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 60)
                print(f"⚠️ Rate Limit! Waiting {retry_after}s")
                time.sleep(retry_after)
            
            elif response.status_code == 401:
                print("🚨 التوكن انتهى أو خطأ!")
                log_to_discord(webhook_url, "❌ خطأ: التوكن غير صالحة!")
                break

        except Exception as e:
            print(f"📡 خطأ اتصال: {e}")
        
        # وقت انتظار متوازن (بين 50-70 ثانية للأمان)
        time.sleep(random.randint(50, 70))

if __name__ == "__main__":
    # تشغيل البوت في خلفية Flask
    threading.Thread(target=sniper, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
