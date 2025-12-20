import os, random, time, requests, threading
from flask import Flask
from datetime import datetime, timezone, timedelta

app = Flask('')
# أضفنا قائمة لآخر اليوزرات المفحوصة
stats = {"checked": 0, "found": 0, "start_time": time.time(), "msg_id": None, "last_users": []}
IMG_URL = "https://r.jina.ai/i/6f9e984d72864b97a2e7c4f1c1f0f4a1"

@app.route('/')
def home():
    return "🚀 Live Update Sniper is Active!"

def manage_webhook_msg():
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url: return

    now = datetime.now(timezone.utc)
    # تنسيق قائمة آخر اليوزرات بشكل مرتب
    users_list = "\n".join([f"┣ 🔍 `{u}`" for u in stats["last_users"][-5:]]) if stats["last_users"] else "┣ جاري البدء..."
    
    embed = {
        "title": "✨ نظام سنايبر الهنداوية الملكي",
        "description": f"```ansi\n[1;34mجاري الفحص الآن عن:[0m\n{users_list}\n```",
        "color": 16776960,
        "image": {"url": IMG_URL},
        "fields": [
            {"name": "⚙️ الحالة", "value": "🟢 `ONLINE`", "inline": True},
            {"name": "🛰️ Latency", "value": f"`{random.randint(40, 120)}ms`", "inline": True},
            {"name": "📊 الإحصائيات", "value": f"┣ المفحوص: `{stats['checked']}`\n┗ الصيد: `{stats['found']}`", "inline": False},
            {"name": "🕒 تحديث تلقائي", "value": f"آخر تحديث: <t:{int(now.timestamp())}:R>", "inline": False}
        ],
        "footer": {"text": "Live Update System • v4.5"}
    }

    payload = {"embeds": [embed]}
    try:
        if stats["msg_id"] is None:
            r = requests.post(f"{webhook_url}?wait=true", json=payload)
            if r.status_code in [200, 201]: stats["msg_id"] = r.json()['id']
        else:
            requests.patch(f"{webhook_url}/messages/{stats['msg_id']}", json=payload)
    except: pass

def get_gold_user():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    pats = [
        lambda: f"{random.choice(chars)}.{random.choice(chars)}{random.choice(chars)}",
        lambda: f"{random.choice(chars)}{random.choice(chars)}.{random.choice(chars)}",
        lambda: f"{random.choice(chars)}_{random.choice(chars)}{random.choice(chars)}"
    ]
    return random.choice(pats)()

def check_loop():
    token = os.getenv('DISCORD_TOKEN')
    headers = {'Authorization': token}
    
    last_ui_update = time.time()

    while True:
        user = get_gold_user()
        stats["last_users"].append(user) # إضافة اليوزر للقائمة
        if len(stats["last_users"]) > 5: stats["last_users"].pop(0) # الاحتفاظ بآخر 5 فقط

        try:
            r = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={user}', headers=headers, timeout=10)
            stats["checked"] += 1
            
            if r.status_code == 200 and r.json().get('is_unique'):
                stats["found"] += 1
                requests.post(os.getenv('WEBHOOK_URL'), json={
                    "content": "@everyone 🎯 صيد ملكي!",
                    "embeds": [{"title": "💎 تم الصيد!", "description": f"اليوزر: `{user}`", "color": 5763719}]
                })
            elif r.status_code == 429:
                time.sleep(r.json().get('retry_after', 60))
        except: pass
        
        # تحديث الرسالة كل دقيقتين (120 ثانية) عشان تظهر اليوزرات الجديدة
        if time.time() - last_ui_update >= 120:
            manage_webhook_msg()
            last_ui_update = time.time()

        time.sleep(random.randint(45, 75))

if __name__ == "__main__":
    threading.Thread(target=check_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
