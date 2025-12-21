import os, random, time, requests, threading
from flask import Flask
from datetime import datetime

app = Flask('')
# إحصائيات منفصلة لكل منصة
stats = {
    "discord": {"checked": 0, "found": 0},
    "instagram": {"checked": 0, "found": 0},
    "twitter": {"checked": 0, "found": 0}
}

@app.route('/')
def home(): return "🚀 System is Online and Scouting..."

def send_to_discord(webhook_url, title, user, platform, color):
    # إرسال رسالة احترافية ومنظمة لكل صيد
    payload = {
        "content": "@everyone" if platform == "Discord" else "",
        "embeds": [{
            "title": title,
            "description": f"🎯 **يوزر جديد متاح!**\n\n👤 **اليوزر:** `{user}`\n🌐 **المنصة:** {platform}\n⏰ **الوقت:** {datetime.now().strftime('%H:%M:%S')}",
            "color": color,
            "footer": {"text": "Multi-Sniper v2025"}
        }]
    }
    requests.post(webhook_url, json=payload)

def sniper_engine():
    token = os.getenv('DISCORD_TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')
    
    # أحرف الديسكورد (4) وأحرف السوشيال (5)
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    social_chars = "abcdefghijklmnopqrstuvwxyz0123456789._"

    # رسالة تشغيل لمرة واحدة فقط
    requests.post(webhook_url, json={"content": "✅ **تم تفعيل الرادار الشامل (ديسكورد + انستا + تويتر)**\nجاري البدء بأحدث إصدار 2025..."})

    while True:
        try:
            # --- 1. فحص ديسكورد ---
            d_user = "".join(random.choices(chars, k=4))
            r_d = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={d_user}', 
                               headers={'Authorization': token}, timeout=5)
            stats["discord"]["checked"] += 1
            if r_d.status_code == 200 and r_d.json().get('is_unique'):
                send_to_discord(webhook_url, "🚨 صيد ديسكورد رباعي!", d_user, "Discord", 5814783)
                stats["discord"]["found"] += 1

            # --- 2. فحص انستقرام (خماسي) ---
            i_user = "".join(random.choices(social_chars, k=5))
            r_i = requests.get(f"https://www.instagram.com/{i_user}/", timeout=5)
            stats["instagram"]["checked"] += 1
            if r_i.status_code == 404:
                send_to_discord(webhook_url, "📸 صيد انستقرام خماسي!", i_user, "Instagram", 15258703)
                stats["instagram"]["found"] += 1

            # --- 3. فحص تويتر (خماسي) ---
            t_user = "".join(random.choices(social_chars, k=5))
            r_t = requests.get(f"https://twitter.com/{t_user}", timeout=5)
            stats["twitter"]["checked"] += 1
            if r_t.status_code == 404:
                send_to_discord(webhook_url, "🐦 صيد تويتر خماسي!", t_user, "Twitter", 1942002)
                stats["twitter"]["found"] += 1

        except: pass
        
        # وقت انتظار ذكي: يفحص يوزرات مختلفة كل 45 ثانية
        time.sleep(random.randint(40, 50))

if __name__ == "__main__":
    threading.Thread(target=sniper_engine, daemon=True).start()
    # استخدام البورت المطلوب لمنع تعليق رندر
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
