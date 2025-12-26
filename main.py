import os
import asyncio
import random
import string
import logging
from datetime import datetime, timedelta
from curl_cffi import requests as requests_async
from fastapi import FastAPI
import uvicorn

# ====== إعدادات البيئة ======
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# الإعدادات اللي اخترتها (30-60 ثانية) ممتازة للأمان بدون بروكسي
DELAY_MIN = float(os.getenv("DELAY_MIN", 30))
DELAY_MAX = float(os.getenv("DELAY_MAX", 60))

# إعداد اللوج لمعرفة ما يحدث بدقة
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ALLOWED_CHARS = string.ascii_lowercase + string.digits + "._"

def generate_username():
    """توليد يوزر عشوائي بطول 2-4 حروف"""
    while True:
        length = random.randint(2, 4)
        username = "".join(random.choice(ALLOWED_CHARS) for _ in range(length))
        if username[0].isalnum() and username[-1].isalnum():
            return username

async def notify_available(username):
    """إرسال إشعار للويب هوك عند إيجاد يوزر متاح"""
    if not WEBHOOK_URL: return
    payload = {
        "content": "@everyone 🟢 **لقطة جديدة!**",
        "embeds": [{
            "title": "Username Available!",
            "description": f"اليوزر المتاح: `{username}`",
            "color": 0x2ecc71,
            "footer": {"text": "Discord Username Checker"},
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    try:
        # إرسال إشعار الويب هوك بشكل منفصل
        from curl_cffi import requests
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        logging.warning(f"⚠️ Webhook notification failed: {e}")

class DiscordScanner:
    def __init__(self, token):
        self.token = token.strip() if token else ""
        self.next_retry = datetime.now()
        self.impersonate = "chrome120" # محاكاة متصفح حقيقي لتجنب الكشف

    async def check(self, username):
        # التأكد من عدم تجاوز وقت الحظر (Rate Limit)
        if datetime.now() < self.next_retry:
            wait_needed = (self.next_retry - datetime.now()).total_seconds()
            await asyncio.sleep(wait_needed)

        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Discord-Locale": "en-US",
            "Referer": "https://discord.com/register",
            "Origin": "https://discord.com"
        }

        try:
            # استخدام curl_cffi لمحاكاة بصمة المتصفح (JA3)
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: requests_async.post(
                "https://discord.com/api/v9/unique-username/registration-check",
                json={"username": username},
                headers=headers,
                impersonate=self.impersonate,
                timeout=15
            ))
        except Exception as e:
            logging.error(f"❌ Network error: {e}")
            return

        # التعامل مع Rate Limit (429)
        if r.status_code == 429:
            try:
                data = r.json()
                wait = float(data.get("retry_after", 60))
            except:
                wait = 60
            self.next_retry = datetime.now() + timedelta(seconds=wait + 5)
            logging.warning(f"⏳ Rate limited! Sleeping for {wait}s...")
            return

        # التعامل مع النجاح (200)
        if r.status_code == 200:
            try:
                data = r.json()
                if data.get("taken") is False:
                    logging.info(f"🟢 [AVAILABLE] {username}")
                    await notify_available(username)
                else:
                    logging.info(f"🔴 [TAKEN] {username}")
            except Exception:
                logging.warning(f"⚠️ Received non-JSON response for {username}")
        
        elif r.status_code in [401, 403]:
            logging.error("💀 Token Invalid or Flagged. Please check your TOKEN!")
        else:
            logging.warning(f"⚠️ Unexpected status {r.status_code} for {username}")

    async def run_scanner(self):
        logging.info("🚀 Scanner is starting with safe delays...")
        while True:
            name = generate_username()
            await self.check(name)
            # التأخير العشوائي الموزع (30-60 ثانية)
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

# --- إعداد FastAPI لضمان بقاء Render شغالاً ---
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "running", "worker": "active", "time": datetime.now().isoformat()}

async def main():
    # تشغيل الفحص كـ Background Task
    asyncio.create_task(DiscordScanner(TOKEN).run_scanner())
    
    # تشغيل خادم FastAPI
    port = int(os.getenv("PORT", 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
