import os, random, time, requests, threading
from flask import Flask
from datetime import datetime, timezone

app = Flask('')
stats = {"checked": 0, "found": 0, "msg_id": None, "current_user": "جاري البدء...", "last_users": []}
IMG_URL = "https://r.jina.ai/i/6f9e984d72864b97a2e7c4f1c1f0f4a1"

@app.route('/')
def home(): return "🛰️ Sniper v15.0 - Pure 4-Chars (SAFE MODE)"

def manage_webhook_msg():
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url: return
    now = datetime.now(timezone.utc)
    users_display = "\n".join([f"┣ 🔍 `{u}`" for u in stats["last_users"][-3:]])
    embed = {
        "title": "🎯 رادار الرباعي الصافي (abcd)",
        "description": f"```ansi\n[1;34mجاري قحص:[0m [1;37m{stats['current_user']}[0m\n\n[1;30mالسجل (رباعي فقط):[0m\n{users_display}\n```",
        "color": 3066993, # لون أخضر غامق للأمان
        "fields": [
            {"name": "📊 الإحصائيات", "value": f"┣ المفحوص: `{stats['checked']}`\n┗ الصيد: `{stats['found']}`", "inline": True},
            {"name": "🕒 آخر تحديث", "value": f"<t:{int(now.timestamp())}:R>", "inline": True},
            {"name": "🛡️ وضع الحماية", "value": "🟢 `MAX_SECURITY`", "inline": False}
        ],
        "footer": {"text": "Only 4-Chars | Safe Speed Active"}
    }
    try:
        if stats["msg_id"] is None:
            r = requests.post(f"{webhook_url}?wait=true", json={"embeds": [embed]})
            if r.status_code in [200, 201]: stats["msg_id"] = r.json()['id']
        else:
            requests.patch(f"{webhook_url}/messages/{stats['msg_id']}", json={"embeds": [embed]})
    except: pass

def get_pure_4():
    # يولد حصراً 4 خانات حروف وأرقام متصلة فقط
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choices(chars, k=4))

def check_loop():
    token = os.getenv('DISCORD_TOKEN')
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    manage_webhook_msg()
    last_ui_update = time.time()
    
    while True:
        user = get_pure_4()
        stats["current_user"] = user
        
        try:
            # الفحص الرسمي
            r = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={user}', headers=headers, timeout=10)
            stats["checked"] += 1
            stats["last_users"].append(user)
            if len(stats["last_users"]) > 5: stats["last_users"].pop(0)

            # إذا لقى علامة الصح الخضراء المتاحة
            if r.status_code == 200 and r.json().get('is_unique'):
                stats["found"] += 1
                requests.post(os.getenv('WEBHOOK_URL'), json={
                    "content": f"@everyone 🎯 لقيت رباعي صافي متاح: `{user}`",
                    "embeds": [{"title": "💎 تم الصيد!", "description": f"اليوزر: `{user}`", "color": 5763719}]
                })
                print(f"✅ SUCCESS: {user}")
            elif r.status_code == 429: # في حال ديسكورد طلب التوقف
                wait_time = r.json().get('retry_after', 60)
                time.sleep(wait_time)
        except: pass
        
        # تحديث الرسالة كل دقيقتين عشان الروم يبقى نظيف
        if time.time() - last_ui_update >= 120:
            manage_webhook_msg()
            last_ui_update = time.time()
            
        # 🛡️ وقت الانتظار الآمن: بين دقيقة ودقيقة وربع (60-80 ثانية)
        # هذا يخلي البوت يفحص بشكل طبيعي كأنه إنسان وما يعرض حسابك للخطر
        time.sleep(random.randint(60, 80))

if __name__ == "__main__":
    threading.Thread(target=check_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
