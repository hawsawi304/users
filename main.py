import os
import time
import random
import requests
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "High-Accuracy Humanoid Sniper is Online"

# --- الإعدادات (تأكد من وضعها في Render) ---
TOKEN = os.getenv("DISCORD_TOKEN") # توكن حسابك الشخصي
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MY_ID = os.getenv("YOUR_USER_ID")

def check_internal_api(target):
    # هذا هو "الـ API الداخلي" الذي يستخدمه المستخدم العادي عند البحث عن صديق
    url = f"https://discord.com/api/v9/users/search?query={target}"
    headers = {
        "Authorization": TOKEN,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            # المنطق الذهبي: إذا لم يوجد أي مستخدم بهذا الاسم تماماً
            is_taken = any(u.get("username", "").lower() == target.lower() for u in users)
            return not is_taken # إذا لم يكن مأخوذاً، فهو متاح
            
        elif response.status_code == 429: # حظر مؤقت (Rate Limit)
            wait = response.json().get("retry_after", 60)
            print(f"⚠️ ديسكورد كشف السرعة! انتظر {wait} ثانية")
            time.sleep(wait)
        elif response.status_code == 401:
            print("❌ التوكن غير صحيح أو انتهت صلاحيته")
            
    except Exception as e:
        print(f"Error: {e}")
    return False

def generate_rare_name():
    # توليد يوزر 4 أزرار (3 حروف + رمز/رقم) لزيادة الندرة
    chars = "abcdefghijklmnopqrstuvwxyz"
    symbols = "._0123456789"
    name = "".join(random.choice(chars) for _ in range(3)) + random.choice(symbols)
    return name

def start_hunting():
    print("🚀 بدأ نظام البحث عالي الدقة (محاكاة بشرية)...")
    while True:
        target = generate_rare_name()
        
        # الفحص عبر النظام الداخلي
        if check_internal_api(target):
            # صيد مؤكد بنسبة عالية!
            payload = {
                "content": f"<@{MY_ID}> 🎯 **صيد عالي الدقة (80% متاح)!**\nالاسم: `{target}`\nافحصه الآن يدوياً!",
                "username": "Ultra Sniper (Self-Mode)"
            }
            requests.post(WEBHOOK_URL, json=payload)
            print(f"✅ تم العثور على: {target}")
            # استراحة طويلة بعد الصيد عشان ما ننكشف
            time.sleep(random.randint(60, 120))
        
        # أهم جزء: الفواصل الزمنية "البشرية"
        # البحث يأخذ بين 25 إلى 45 ثانية (بطيء لكن آمن ودقيق)
        time.sleep(random.uniform(25, 45))
        
        # استراحة "القهوة": كل 15 فحص، توقف تماماً لمدة 10 دقائق
        if random.random() < 0.05: # احتمالية عشوائية للاستراحة
            print("☕ استراحة محاكاة للبشر لمدة 10 دقائق...")
            time.sleep(600)

# تشغيل في الخلفية
Thread(target=start_hunting, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
