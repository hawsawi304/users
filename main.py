import os, random, time, requests, threading
from flask import Flask
from datetime import datetime, timezone

app = Flask('')
stats = {"checked": 0, "found": 0, "msg_id": None, "current_user": "جاري البدء...", "last_users": []}
IMG_URL = "https://r.jina.ai/i/6f9e984d72864b97a2e7c4f1c1f0f4a1"

@app.route('/')
def home(): return "🛰️ Sniper v13.0 - Hybrid Mode ACTIVE"

def manage_webhook_msg():
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url: return
    now = datetime.now(timezone.utc)
    users_display = "\n".join([f"┣ 🔍 `{u}`" for u in stats["last_users"][-3:]])
    embed = {
        "title": "✨ نظام سنايبر الهنداوية الملكي",
        "description": f"```ansi\n[1;34mجاري قنص:[0m [1;37m{stats['current_user']}[0m\n\n[1;30mالسجل الأخير (4 خانات أو أقل):[0m\n{users_display}\n```",
        "color": 16776960,
        "image": {"url": IMG_URL},
        "fields": [
            {"name": "⚙️ الحالة", "value": "🟢 `ONLINE`", "inline": True},
            {"name": "📊 الإحصائيات", "value": f"┣ المفحوص: `{stats['checked']}`\n┗ الصيد: `{stats['found']}`", "inline": False},
            {"name": "🕒 تحديث الرادار", "value": f"<t:{int(now.timestamp())}:R>", "inline": False}
        ],
        "footer": {"text": "Max 4-Chars | No symbols padding"}
    }
    try:
        if stats["msg_id"] is None:
            r = requests.post(f"{webhook_url}?wait=true", json={"embeds": [embed]})
            if r.status_code in [200, 201]: stats["msg_id"] = r.json()['id']
        else:
            requests.patch(f"{webhook_url}/messages/{stats['msg_id']}", json={"embeds": [embed]})
    except: pass

def get_target_user():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    c = lambda k: "".join(random.choices(chars, k=k))
    
    # أنماط ديسكورد الرسمية (4 خانات أو أقل فقط)
    patterns = [
        lambda: c(4),           # رباعي صافي (ab12)
        lambda: f"{c(3)}_ ",    # ثلاثي بشرطة (abc_)
        lambda: f"{c(3)}.",     # ثلاثي بنقطة (abc.)
        lambda: f"{c(2)}_{c(1)}", # منسق (ab_c)
        lambda: f"{c(1)}.{c(2)}", # منسق (a.bc)
        lambda: c(3)            # ثلاثي صافي (abc)
    ]
    # تنظيف أي مسافات زائدة وضمان الطول
    user = random.choice(patterns)().replace(" ", "")
    return user[:4] # تأكيد نهائي أن الطول لا يزيد عن 4

def check_loop():
    token = os.getenv('DISCORD_TOKEN')
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    manage_webhook_msg()
    last_ui_update = time.time()
    
    while True:
        user = get_target_user()
        stats["current_user"] = user
        
        try:
            # الفحص المزدوج لضمان عدم "فغرة" البوت
            r = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={user}', headers=headers, timeout=10)
            stats["checked"] += 1
            
            stats["last_users"].append(user)
            if len(stats["last_users"]) > 5: stats["last_users"].pop(0)

            # إذا رد ديسكورد بأن اليوزر فريد ومتاح
            if r.status_code == 200:
                is_unique = r.json().get('is_unique')
                if is_unique:
                    stats["found"] += 1
                    requests.post(os.getenv('WEBHOOK_URL'), json={
                        "content": f"@everyone 🎯 صيد حقيقي! اليوزر متاح الحين: `{user}`",
                        "embeds": [{"title": "💎 صيد ملكي", "description": f"اليوزر: `{user}`\nالنوع: 4 خانات أو أقل", "color": 5763719}]
                    })
            elif r.status_code == 429: # في حال الحظر المؤقت
                time.sleep(r.json().get('retry_after', 60))
        except: pass
        
        if time.time() - last_ui_update >= 120:
            manage_webhook_msg()
            last_ui_update = time.time()
            
        # سرعة فحص متوازنة للحفاظ على التوكن
        time.sleep(random.randint(40, 60))

if __name__ == "__main__":
    threading.Thread(target=check_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
