import os, random, time, requests, threading
from flask import Flask

app = Flask('')
@app.route('/')
def home(): return "FINAL_ULTIMATE_SNIPER_V10"

# نظام الهيدرز الذكي لمحاكاة التطبيقات الرسمية
def get_headers(platform):
    if platform == "instagram":
        return {
            "User-Agent": "Instagram 219.0.0.12.117 Android",
            "X-IG-App-ID": "936619743392459"
        }
    elif platform == "discord":
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1"
    }

def send_found_embed(webhook, platform, user):
    # إعدادات الألوان والأيقونات لكل منصة
    config = {
        "discord": {
            "color": 0x5865F2,
            "icon": "https://cdn-icons-png.flaticon.com/512/2111/2111370.png",
            "name": "Discord"
        },
        "instagram": {
            "color": 0xE1306C,
            "icon": "https://cdn-icons-png.flaticon.com/512/174/174855.png",
            "name": "Instagram"
        },
        "twitter": {
            "color": 0x1DA1F2,
            "icon": "https://cdn-icons-png.flaticon.com/512/733/733579.png",
            "name": "Twitter/X"
        }
    }
    
    cfg = config.get(platform)
    payload = {
        "username": "AI Elite Sniper",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/8132/8132334.png",
        "content": "@everyone",
        "embeds": [{
            "title": "🎯 صيد جديد متاح الحين!",
            "description": f"استعجل وسجل اليوزر قبل يطير عليك 🚀",
            "color": cfg["color"],
            "thumbnail": {"url": cfg["icon"]},
            "fields": [
                {"name": "👤 اليوزر", "value": f"**`{user}`**", "inline": True},
                {"name": "🌐 المنصة", "value": f"**{cfg['name']}**", "inline": True},
                {"name": "📊 الحالة", "value": "🟢 متاح للتسجيل", "inline": False}
            ],
            "footer": {"text": "نظام الفحص المباشر | AI Sniper V10"},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }
    try:
        requests.post(webhook, json=payload)
    except: pass

import datetime

def sniper_engine(webhook):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    social_chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    
    while True:
        # 1. ديسكورد (4 خانات فقط)
        target_dc = "".join(random.choices(chars, k=4))
        try:
            r = requests.post("https://discord.com/api/v9/unique-username/username-attempt-unauthed", 
                            json={"username": target_dc}, headers=get_headers("discord"), timeout=5)
            if r.status_code == 200 and r.json().get("taken") == False:
                send_found_embed(webhook, "discord", target_dc)
        except: pass

        # 2. انستقرام (5 خانات) - فحص التوفر المباشر
        target_ig = "".join(random.choices(social_chars, k=5))
        try:
            r = requests.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target_ig}", 
                            headers=get_headers("instagram"), timeout=5)
            if r.status_code == 404:
                send_found_embed(webhook, "instagram", target_ig)
        except: pass

        # 3. تويتر (5 خانات) - فحص التوفر المباشر
        target_tw = "".join(random.choices(chars, k=5))
        try:
            # رابط فحص التوفر الرسمي لتويتر
            r = requests.get(f"https://twitter.com/i/api/i/users/username_available.json?username={target_tw}", 
                            headers=get_headers("twitter"), timeout=5)
            if (r.status_code == 200 and r.json().get("valid") == True) or r.status_code == 404:
                send_found_embed(webhook, "twitter", target_tw)
        except: pass

        time.sleep(20) # توقيت حماية السيرفر من الحظر

if __name__ == "__main__":
    webhook = os.getenv('WEBHOOK_URL')
    if webhook:
        threading.Thread(target=sniper_engine, args=(webhook,), daemon=True).start()
        app.run(host='0.0.0.0', port=10000)
