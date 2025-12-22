import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask('')
stats = {"dc_c": 0, "dc_f": 0, "ig_c": 0, "ig_f": 0}

@app.route('/')
def home(): return "PROTECTION_BYPASS_V33"

# هيدرز "نخاع" النظام - تحاكي متصفح سفاري على آيفون 17 بدقة
H = {
    "Accept": "application/json",
    "Accept-Language": "ar-SA,en-US;q=0.9",
    "Connection": "keep-alive",
    "Host": "discord.com",
    "Origin": "https://discord.com",
    "Referer": "https://discord.com/register",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
}

def notify(webhook, platform, user):
    # منشن @everyone فوري عند الصيد
    try:
        payload = {"content": f"🚨 @everyone \n🎯 **صيد {platform} نادِر!** \n✅ اليوزر: **`{user}`**"}
        requests.post(webhook, json=payload, timeout=5)
    except: pass

def update_ui(webhook):
    m_id = None
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار الاختراق (V33)",
                    "description": "تم تفعيل وضع محاكاة التسجيل البشري",
                    "fields": [
                        {"name": "Discord (4 Chars)", "value": f"📊 `{stats['dc_c']}` | 🎯 `{stats['dc_f']}`", "inline": True},
                        {"name": "Instagram (5 Chars)", "value": f"📊 `{stats['ig_c']}` | 🎯 `{stats['ig_f']}`", "inline": True}
                    ],
                    "color": 0xe74c3c,
                    "footer": {"text": "System Active | No Detection"},
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }]
            }
            if m_id is None:
                r = requests.post(webhook + "?wait=true", json=payload)
                m_id = r.json()['id']
            else:
                requests.patch(f"{webhook}/messages/{m_id}", json=payload)
        except: pass
        time.sleep(25)

def dc_bypass(webhook):
    # الحروف والأرقام للفحص
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    while True:
        try:
            u = "".join(random.choices(chars, k=4))
            # ضرب رابط التسجيل (الباب الخلفي)
            r = requests.post("https://discord.com/api/v9/auth/register/check-username", 
                            json={"username": u}, headers=H, timeout=5)
            stats["dc_c"] += 1
            
            # إذا الرد 200 يعني اليوزر "غير موجود" ومتاح للتسجيل
            if r.status_code == 200:
                stats["dc_f"] += 1
                notify(webhook, "Discord", u)
            
            # سرعة "المنطقة الرمادية" (ثانية ونصف بين كل طلب)
            time.sleep(1.5)
        except: time.sleep(10)

def ig_bypass(webhook):
    while True:
        try:
            u = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
            # رابط التحقق الداخلي لتطبيق انستا
            r = requests.post("https://www.instagram.com/api/v1/users/check_username/", 
                            data={"username": u}, headers=H, timeout=5)
            stats["ig_c"] += 1
            if r.status_code == 200 and r.json().get("available") == True:
                stats["ig_f"] += 1
                notify(webhook, "Instagram", u)
            time.sleep(15)
        except: time.sleep(10)

if __name__ == "__main__":
    url = os.getenv('WEBHOOK_URL')
    if url:
        threading.Thread(target=update_ui, args=(url,), daemon=True).start()
        threading.Thread(target=dc_bypass, args=(url,), daemon=True).start()
        threading.Thread(target=ig_bypass, args=(url,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
