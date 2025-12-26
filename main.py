import os
import asyncio
import random
import string
import logging
from datetime import datetime, timedelta
from curl_cffi import requests as requests_async # محاكاة البصمة
from fastapi import FastAPI
import uvicorn

# ====== ENV (تأكد من ضبطها في Render) ======
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DELAY_MIN = float(os.getenv("DELAY_MIN", 5)) # زدنا التأخير للأمان
DELAY_MAX = float(os.getenv("DELAY_MAX", 10))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ALLOWED_CHARS = string.ascii_lowercase + string.digits + "._"

def generate_username():
    while True:
        length = random.randint(2, 4)
        username = "".join(random.choice(ALLOWED_CHARS) for _ in range(length))
        if username[0].isalnum() and username[-1].isalnum():
            return username

async def notify_available(username):
    if not WEBHOOK_URL: return
    payload = {
        "content": "@everyone",
        "embeds": [{
            "title": "🟢 USERNAME AVAILABLE",
            "description": f"User: `{username}`",
            "color": 0x2ecc71,
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    try:
        # هنا نستخدم requests عادية للويب هوك لا بأس
        from curl_cffi import requests
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        logging.warning(f"⚠️ Webhook error: {e}")

class DiscordScanner:
    def __init__(self, token):
        self.token = token.strip() if token else ""
        self.next_retry = datetime.now()
        # محاكاة بصمة كروم 120 (عالمية)
        self.impersonate = "chrome120" 

    async def check(self, username):
        if datetime.now() < self.next_retry:
            wait_needed = (self.next_retry - datetime.now()).total_seconds()
            await asyncio.sleep(wait_needed)

        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Discord-Locale": "en-US",
            "Referer": "https://discord.com/register"
        }

        try:
            # استخدام curl_cffi لتجاوز حماية الـ TLS Fingerprinting
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: requests_async.post(
                "https://discord.com/api/v9/unique-username/registration-check",
                json={"username": username},
                headers=headers,
                impersonate=self.impersonate,
                timeout=15
            ))
        except Exception as e:
            logging.error(f"❌ Network/SSL error: {e}")
            return

        if r.status_code == 429:
            try:
                data = r.json()
                wait = float(data.get("retry_after", 60))
            except:
                wait = 60
            self.next_retry = datetime.now() + timedelta(seconds=wait + 5)
            logging.warning(f"⏳ Rate limited! Sleeping for {wait}s")
            return

        if r.status_code == 200:
            try:
                data = r.json()
                if data.get("taken") is False:
                    logging.info(f"🟢 [AVAILABLE] {username}")
                    await notify_available(username)
                else:
                    logging.info(f"🔴 [TAKEN] {username}")
            except:
                logging.warning(f"⚠️ Invalid JSON response for {username}")
        elif r.status_code == 403 or r.status_code == 401:
            logging.error("💀 Token is Invalid or Flagged by Discord!")
        else:
            logging.warning(f"⚠️ Status {r.status_code} for {username}")

    async def run(self):
        logging.info("🚀 Scanner started...")
        while True:
            name = generate_username()
            await self.check(name)
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "running", "timestamp": datetime.now().isoformat()}

async def main():
    scanner = DiscordScanner(TOKEN)
    # تشغيل الفحص في الخلفية
    asyncio.create_task(scanner.run())
    
    # تشغيل خادم FastAPI (مهم لـ Render)
    port = int(os.getenv("PORT", 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())import os
import asyncio
import random
import string
import logging
from datetime import datetime, timedelta
from curl_cffi import requests as requests_async # محاكاة البصمة
from fastapi import FastAPI
import uvicorn

# ====== ENV (تأكد من ضبطها في Render) ======
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DELAY_MIN = float(os.getenv("DELAY_MIN", 5)) # زدنا التأخير للأمان
DELAY_MAX = float(os.getenv("DELAY_MAX", 10))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ALLOWED_CHARS = string.ascii_lowercase + string.digits + "._"

def generate_username():
    while True:
        length = random.randint(2, 4)
        username = "".join(random.choice(ALLOWED_CHARS) for _ in range(length))
        if username[0].isalnum() and username[-1].isalnum():
            return username

async def notify_available(username):
    if not WEBHOOK_URL: return
    payload = {
        "content": "@everyone",
        "embeds": [{
            "title": "🟢 USERNAME AVAILABLE",
            "description": f"User: `{username}`",
            "color": 0x2ecc71,
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    try:
        # هنا نستخدم requests عادية للويب هوك لا بأس
        from curl_cffi import requests
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        logging.warning(f"⚠️ Webhook error: {e}")

class DiscordScanner:
    def __init__(self, token):
        self.token = token.strip() if token else ""
        self.next_retry = datetime.now()
        # محاكاة بصمة كروم 120 (عالمية)
        self.impersonate = "chrome120" 

    async def check(self, username):
        if datetime.now() < self.next_retry:
            wait_needed = (self.next_retry - datetime.now()).total_seconds()
            await asyncio.sleep(wait_needed)

        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "X-Discord-Locale": "en-US",
            "Referer": "https://discord.com/register"
        }

        try:
            # استخدام curl_cffi لتجاوز حماية الـ TLS Fingerprinting
            loop = asyncio.get_event_loop()
            r = await loop.run_in_executor(None, lambda: requests_async.post(
                "https://discord.com/api/v9/unique-username/registration-check",
                json={"username": username},
                headers=headers,
                impersonate=self.impersonate,
                timeout=15
            ))
        except Exception as e:
            logging.error(f"❌ Network/SSL error: {e}")
            return

        if r.status_code == 429:
            try:
                data = r.json()
                wait = float(data.get("retry_after", 60))
            except:
                wait = 60
            self.next_retry = datetime.now() + timedelta(seconds=wait + 5)
            logging.warning(f"⏳ Rate limited! Sleeping for {wait}s")
            return

        if r.status_code == 200:
            try:
                data = r.json()
                if data.get("taken") is False:
                    logging.info(f"🟢 [AVAILABLE] {username}")
                    await notify_available(username)
                else:
                    logging.info(f"🔴 [TAKEN] {username}")
            except:
                logging.warning(f"⚠️ Invalid JSON response for {username}")
        elif r.status_code == 403 or r.status_code == 401:
            logging.error("💀 Token is Invalid or Flagged by Discord!")
        else:
            logging.warning(f"⚠️ Status {r.status_code} for {username}")

    async def run(self):
        logging.info("🚀 Scanner started...")
        while True:
            name = generate_username()
            await self.check(name)
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "running", "timestamp": datetime.now().isoformat()}

async def main():
    scanner = DiscordScanner(TOKEN)
    # تشغيل الفحص في الخلفية
    asyncio.create_task(scanner.run())
    
    # تشغيل خادم FastAPI (مهم لـ Render)
    port = int(os.getenv("PORT", 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
