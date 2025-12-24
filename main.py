import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
# إحصائيات النظام
stats = {
    "checked": 0,
    "found": 0,
    "current_user": "جاري البدء...",
    "status": "متصل ✅",
    "start_time": datetime.datetime.now(),
    "msg_id": None # لتخزين معرف رسالة الحالة وتحديثها
}

@app.route('/')
def home(): return "SNIPER_V7_PRO_ONLINE"

def get_ping():
    # حساب تقريبي للبنق بناءً على استجابة جوجل
    try:
        start = time.time()
        requests.get("https://www.google.com", timeout=2)
        return f"{int((time.time() - start) * 1000)}ms"
    except: return "Error"

def update_status_embed(webhook):
    global stats
    while True:
        try:
            uptime = str(datetime.datetime.now() - stats["start_time"]).split('.')[0]
            ping = get_ping()
            
            payload = {
                "embeds": [{
                    "title": "🖥️ لوحة تحكم القناص الشامل V7-PRO",
                    "description": f"يتم فحص اليوزرات (4-5 حروف) حالياً بنجاح.",
                    "color": 0x2ecc71,
                    "fields": [
                        {"name": "📊 المفحوصة", "value": f"`{stats['checked']}`", "inline": True},
                        {"name": "🎯 المصيدة", "value": f"`{stats['found']}`", "inline": True},
                        {"name": "📡 البنق", "value": f"`{ping}`", "inline": True},
                        {"name": "🔍 يفحص الآن", "value": f"`{stats['current_user']}`", "inline": True},
                        {"name": "⏳ وقت التشغيل", "value": f"`{uptime}`", "inline": True},
                        {"name": "🛡️ الحالة", "value": f"`{stats['status']}`", "inline": True}
                    ],
                    "footer": {"text": "تحديث تلقائي كل 10 ثوانٍ | V7 Pro Mode"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }

            if stats["msg_id"] is None:
                # إرسال رسالة جديدة لأول مرة وحفظ الـ ID
                r = requests.post(webhook + "?wait=true", json=payload)
                stats["msg_id"] = r.json()['id']
            else:
                # تحديث نفس الرسالة السابقة
                requests.patch(f"{webhook}/messages/{stats['msg_id']}", json=payload)
                
        except Exception as e:
            print(f"Error updating embed: {e}")
        
        time.sleep(10) # تحديث لوحة التحكم كل 10 ثوانٍ

def sniper():
    global stats
    webhook = os.getenv('WEBHOOK_URL')
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    
    # تشغيل خيط تحديث الحالة
    threading.Thread(target=update_status_embed, args=(webhook,), daemon=True).start()

    while True:
        try:
            # توليد يوزر (4 أو 5 حروف)
            length = random.choice([4, 5])
            user = "".join(random.choices(chars, k=length))
            stats["current_user"] = user
            
            # فحص ديسكورد (الطريقة السريعة)
            r_dc = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                               json={"username": user}, timeout=5)
            
            stats["checked"] += 1
            
            if r_dc.status_code == 200:
                if r_dc.json().get("taken") == False:
                    stats["found"] += 1
                    # إرسال التنبيه فوراً كرسالة منفصلة مع منشن
                    requests.post(webhook, json={
                        "content": f"🎯 **صيد ديسكورد جديد!**\nاليوزر: `{user}`\nالنوع: {length} حروف\n@everyone"
                    })
            elif r_dc.status_code == 429:
                stats["status"] = "معدل محدود (Rate Limit) ⚠️"
                time.sleep(30)
                stats["status"] = "متصل ✅"

        except:
            stats["status"] = "خطأ في الاتصال ❌"
            time.sleep(5)
            stats["status"] = "متصل ✅"
        
        time.sleep(2) # سرعة V7 المعهودة

if __name__ == "__main__":
    threading.Thread(target=sniper, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
