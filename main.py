import os, random, time, requests, threading
from flask import Flask
from datetime import datetime

app = Flask('')
stats = {
    "discord": {"checked": 0, "found": 0, "msg_id": None},
    "instagram": {"checked": 0, "found": 0, "msg_id": None},
    "twitter": {"checked": 0, "found": 0, "msg_id": None}
}

def update_embed(webhook_url, platform):
    color = {"discord": 5814783, "instagram": 15258703, "twitter": 1942002}[platform]
    data = stats[platform]
    
    payload = {
        "embeds": [{
            "title": f"📊 رادار {platform.capitalize()}",
            "description": f"┣ **المفحوص:** `{data['checked']}`\n┗ **الصيد:** `{data['found']}`",
            "color": color,
            "footer": {"text": f"آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"}
        }]
    }
    
    if data["msg_id"] is None:
        # إرسال رسالة جديدة لأول مرة
        r = requests.post(f"{webhook_url}?wait=true", json=payload)
        if r.status_code in [200, 201]:
            data["msg_id"] = r.json()['id']
    else:
        # تحديث الرسالة الموجودة (لتقليل الإزعاج)
        requests.patch(f"{webhook_url}/messages/{data['msg_id']}", json=payload)

def sniper_engine():
    token = os.getenv('DISCORD_TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')
    
    while True:
        try:
            # 1. ديسكورد
            d_user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=4))
            r_d = requests.get(f'https://discord.com/api/v9/users/@me/suffixes?username={d_user}', headers={'Authorization': token}, timeout=5)
            stats["discord"]["checked"] += 1
            if r_d.status_code == 200 and r_d.json().get('is_unique'):
                requests.post(webhook_url, json={"content": f"@everyone 🚨 **صيد ديسكورد رباعي:** `{d_user}`"})
                stats["discord"]["found"] += 1
            
            # 2. انستقرام
            i_user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789._", k=5))
            r_i = requests.get(f"https://www.instagram.com/{i_user}/", timeout=5)
            stats["instagram"]["checked"] += 1
            if r_i.status_code == 404:
                requests.post(webhook_url, json={"content": f"📸 **صيد انستا خماسي:** `{i_user}`"})
                stats["instagram"]["found"] += 1

            # تحديث الإيمبد كل 10 عمليات فحص عشان ما يجي حظر
            if stats["discord"]["checked"] % 10 == 0:
                for p in ["discord", "instagram"]: update_embed(webhook_url, p)

        except: pass
        time.sleep(random.randint(40, 50))

if __name__ == "__main__":
    threading.Thread(target=sniper_engine, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
