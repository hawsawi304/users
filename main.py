import os, random, time, requests, threading
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "FINAL_MEGA_SNIPER_V7"

REAL_HEADERS = {
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
}

def check_all(user, webhook):
    # 1. ديسكورد (رابط التسجيل المباشر)
    try:
        r_dc = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": user}, headers=REAL_HEADERS, timeout=5)
        if r_dc.status_code == 200 and r_dc.json().get("taken") == False:
            requests.post(webhook, json={"content": f"🎯 **ديسكورد متاح:** `{user}` @everyone"})
    except: pass

    # 2. انستقرام (رابط البيانات السريع)
    try:
        r_ig = requests.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={user}", headers=REAL_HEADERS, timeout=5)
        if r_ig.status_code == 404:
            requests.post(webhook, json={"content": f"📸 **انستقرام متاح:** `{user}` @everyone"})
    except: pass

    # 3. تويتر (رابط البروفايل مع هيدر الجوال)
    try:
        r_tw = requests.get(f"https://www.twitter.com/{user}", headers=REAL_HEADERS, timeout=5)
        if r_tw.status_code == 404:
            requests.post(webhook, json={"content": f"🐦 **تويتر متاح:** `{user}` @everyone"})
    except: pass

def sniper_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        # يولد يوزر رباعي ويفحصه على كل المنصات مرة وحدة
        target = "".join(random.choices(chars, k=4))
        check_all(target, webhook)
        
        # يولد يوزر خماسي (اختياري) لزيادة فرص الصيد في انستا وتويتر
        target_5 = target + random.choice(chars)
        check_all(target_5, webhook)
        
        time.sleep(20) # السرعة هذي هي "الأمان" عشان رندر ما ينحظر IP حقه

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if webhook:
        requests.post(webhook, json={"content": "🔥 **تم تفعيل القناص الشامل V7**\n(ديسكورد - انستا - تويتر)\nالنظام يعمل بنظام فحص التوفر المباشر."})
        threading.Thread(target=sniper_engine, args=(webhook,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
