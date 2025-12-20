import os, random, time, requests, threading
from flask import Flask
from datetime import datetime

app = Flask('')
stats = {"checked": 0, "found": 0, "start_time": time.time()}
IMG_URL = "https://r.jina.ai/i/6f9e984d72864b97a2e7c4f1c1f0f4a1"

@app.route('/')
def home():
    return "Sniper Status: ONLINE"

def get_ping():
    # حساب سرعة الاستجابة مع ديسكورد
    try:
        start = time.time()
        requests.get("https://discord.com/api/v9/gateway")
        return f"{int((time.time() - start) * 1000)}ms"
    except: return "N/A"

def send_webhook(title, description, color, ping_me=False, is_launch=False):
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url: return
    
    content = "@everyone" if ping_me else ""
    
    # بناء الايمبد المرتب
    embed = {
        "title": f"✨ {title}",
        "description": f"```ansi\n{description}\n```",
        "color": color,
        "image": {"url": IMG_URL},
        "fields": [
            {"name": "🛰️ Latency", "value": f"`{get_ping()}`", "inline": True},
            {"name": "⚙️ Status", "value": "🟢 `ONLINE`", "inline": True}
        ],
        "footer": {"text": "Hindawiya Sniper Pro • v3.5", "icon_url": "https://cdn-icons-png.flaticon.com/512/944/944948.png"},
        "timestamp": datetime.utcnow().isoformat()
    }

    # إضافة إحصائيات الفحص فقط في التقارير والصيد
    if not is_launch:
        embed["fields"].append({"name": "📊 Stats", "value": f"Checked: `{stats['checked']}`\nFound: `{stats['found']}`", "inline": False})

    data = {"content": content, "embeds": [embed]}
    try: requests.post(webhook_url, json=data)
    except: pass

def get_gold_user():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    pats = [
        lambda: f"{random.choice(chars)}.{random.choice(chars)}{random.choice(chars)}",
        lambda: f"{random.choice(chars)}{random.choice(chars)}.{random.choice(chars)}",
        lambda: f"{random.choice(chars)}_{random.choice(chars)}{random.choice(chars)}"
    ]
    return random.choice(pats)()

def check_users():
    token = os.getenv('DISCORD_TOKEN')
    headers = {'Authorization': token}
    last_report = time.time()
    
    # --- رسالة التشغيل الفخمة ---
    send_webhook(
        "نظام سنايبر الهنداوية", 
        "[1;34mتم ربط النظام بسيرفرات ديسكورد...\n[1;32mالمعصوب الملكي قيد التحضير\n[1;33mجاري فحص القوائم الذهبية الآن", 
        16776960, 
        is_launch=True
    )

    while True:
        user = get_gold_user()
        try:
            r = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={user}', headers=headers)
            stats["checked"] += 1
            if r.status_code == 200 and r.json().get('is_unique'):
                stats["found"] += 1
                send_webhook("🎯 صيد ملكي جديد!", f"[1;37mاليوزر: [1;32m{user}\n[1;34mالحالة: متاح للتسجيل", 5763719, ping_me=True)
            elif r.status_code == 429:
                time.sleep(r.json().get('retry_after', 60))
        except: pass
        
        if time.time() - last_report >= 3600:
            send_webhook("تقرير الساعة", "[1;37mالبوت يعمل بكفاءة عالية\n[1;32mلا توجد أخطاء تقنية", 3447003)
            last_report = time.time()

        time.sleep(random.randint(45, 80))

if __name__ == "__main__":
    threading.Thread(target=check_users).start()
    app.run(host='0.0.0.0', port=8080)
