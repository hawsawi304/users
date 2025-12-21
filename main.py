import os, random, time, requests, threading
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "SYSTEM_STABLE_2025"

def sniper():
    token = os.getenv('DISCORD_TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')
    session = requests.Session()
    session.headers.update({'Authorization': token, 'Content-Type': 'application/json'})

    # تنبيه هادئ لمرة واحدة فقط
    requests.post(webhook_url, json={"content": "✅ **النظام استقر.** جاري فحص ديسكورد وانستا وتويتر بصمت..."})

    while True:
        try:
            # 1. ديسكورد رباعي
            d_user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
            r = session.get(f'https://discord.com/api/v9/users/@me/suffixes?username={d_user}', timeout=5)
            if r.status_code == 200 and r.json().get('is_unique'):
                requests.post(webhook_url, json={"content": f"@everyone 🎯 **صيد ديسكورد:** `{d_user}`"})

            # 2. انستا/تويتر خماسي
            platform = random.choice(["instagram", "twitter"])
            s_user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
            r_s = requests.get(f"https://www.{platform}.com/{s_user}", timeout=5)
            if r_s.status_code == 404:
                requests.post(webhook_url, json={"content": f"📸 **صيد {platform}:** `{s_user}`"})
        except: pass
        
        time.sleep(random.randint(40, 50))

if __name__ == "__main__":
    threading.Thread(target=sniper, daemon=True).start()
    # إجبار البوت على بورت رندر الأساسي
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
