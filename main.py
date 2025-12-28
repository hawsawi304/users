import os
import asyncio
import random
import string
import logging
from datetime import datetime, timedelta
from curl_cffi import requests as requests_async
from fastapi import FastAPI
import uvicorn

# ====== الإعدادات ======
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DELAY_MIN = float(os.getenv("DELAY_MIN", 30))
DELAY_MAX = float(os.getenv("DELAY_MAX", 60))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

total_scanned = 0
last_user = "None"
status_msg_id = None # تخزين ID الرسالة لتحديثها

def generate_username():
    length = random.randint(3, 4)
    return "".join(random.choice(string.ascii_lowercase + string.digits + "._") for _ in range(length))

async def update_live_status():
    """تحديث الرسالة في ديسكورد كل 10 ثواني"""
    global status_msg_id
    from curl_cffi import requests
    
    # تحويل رابط الويب هوك لرابط يدعم تعديل الرسائل
    edit_url = f"{WEBHOOK_URL}/messages/{status_msg_id}" if status_msg_id else WEBHOOK_URL

    while True:
        payload = {
            "embeds": [{
                "title": "📡 رادار اليوزرات - حالة البث المباشر",
                "description": "هذه الرسالة تتحدث تلقائياً كل فحص.",
                "color": 0x3498db,
                "fields": [
                    {"name": "آخر يوزر تم فحصه", "value": f"`{last_user}`", "inline": True},
                    {"name": "إجمالي الفحص", "value": f"`{total_scanned}`", "inline": True},
                    {"name": "حالة السيرفر", "value": "🟢 يعمل (Render)", "inline": False}
                ],
                "footer": {"text": f"آخر تحديث: {datetime.now().strftime('%H:%M:%S')}"}
            }]
        }

        try:
            if not status_msg_id:
                # أول مرة: نرسل رسالة جديدة (ونضيف wait=true عشان يرجع لنا الـ ID)
                r = requests.post(f"{WEBHOOK_URL}?wait=true", json=payload, timeout=10)
                if r.status_code in [200, 204]:
                    status_msg_id = r.json().get("id")
            else:
                # المرات الجاية: نسوي Edit للرسالة القديمة
                requests.patch(edit_url, json=payload, timeout=10)
        except Exception as e:
            logging.warning(f"⚠️ Status Update Error: {e}")
        
        await asyncio.sleep(10) # تحديث كل 10 ثواني عشان ما تنحظر من ديسكورد

async def notify_available(username):
    # إذا لقى صيدة، يرسل رسالة منفصلة (عشان تجيك منشن)
    payload = {"content": f"@everyone 🟢 **صيدة جديدة: `{username}`**"}
    try:
        from curl_cffi import requests
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except: pass

class DiscordScanner:
    def __init__(self, token):
        self.token = token.strip() if token else ""
        self.next_retry = datetime.now()

    async def check(self, username):
        global total_scanned, last_user
        if datetime.now() < self.next_retry:
            await asyncio.sleep((self.next_retry - datetime.now()).total_seconds())

        url = "https://discord.com/api/v9/users/@me/pomelo-attempt"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}

        try:
            last_user = username
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: requests_async.post(
                url, json={"username": username}, headers=headers, impersonate="chrome120", timeout=15
            ))
            total_scanned += 1
            
            if r.status_code == 429:
                wait = r.json().get("retry_after", 60)
                self.next_retry = datetime.now() + timedelta(seconds=wait + 5)
            elif r.status_code == 200:
                if r.json().get("taken") is False:
                    await notify_available(username)
        except Exception: pass

    async def run(self):
        while True:
            await self.check(generate_username())
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

app = FastAPI()
@app.get("/")
async def health(): return {"status": "ok"}

async def main():
    scanner = DiscordScanner(TOKEN)
    asyncio.create_task(scanner.run())
    asyncio.create_task(update_live_status()) # تشغيل التحديث التلقائي
    
    port = int(os.getenv("PORT", 10000))
    await uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=port)).serve()

if __name__ == "__main__":
    asyncio.run(main())
