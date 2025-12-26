import os
import asyncio
import httpx
import random
import string
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI
import uvicorn

# ====== ENV ======
TOKEN = os.getenv("TOKEN")  # توكن واحد
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DELAY_MIN = float(os.getenv("DELAY_MIN", 2))  # أقل تأخير 2 ثانية
DELAY_MAX = float(os.getenv("DELAY_MAX", 4))  # أعلى تأخير 4 ثواني

# ====== LOGGING ======
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ====== USERNAME GENERATOR ======
ALLOWED_CHARS = string.ascii_lowercase + string.digits + "._"

def generate_username():
    while True:
        length = random.randint(2, 4)  # من 2 إلى 4 حروف
        username = "".join(random.choice(ALLOWED_CHARS) for _ in range(length))
        if username[0].isalnum() and username[-1].isalnum():  # لا يبدأ أو ينتهي بنقطة أو _
            return username

# ====== WEBHOOK ======
async def notify_available(username):
    payload = {
        "content": "@everyone",
        "embeds": [{
            "title": "🟢 USERNAME AVAILABLE",
            "description": f"`{username}`",
            "color": 0x2ecc71
        }]
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(WEBHOOK_URL, json=payload, timeout=10)
        if r.status_code != 204:
            logging.warning(f"⚠️ Webhook returned {r.status_code}")

# ====== ACCOUNT ======
class DiscordAccount:
    def __init__(self, token):
        self.token = token.strip()
        self.client = httpx.AsyncClient(
            http2=True,
            headers={
                "Authorization": self.token,
                "Content-Type": "application/json"
            }
        )
        self.next_retry = datetime.now()

# ====== SCANNER ======
class DiscordScanner:
    def __init__(self, token):
        self.account = DiscordAccount(token)
        self.queue = asyncio.Queue()

    async def producer(self):
        while True:
            await self.queue.put(generate_username())
            await asyncio.sleep(0.5)

    async def check(self, username):
        account = self.account
        if datetime.now() < account.next_retry:
            await self.queue.put(username)
            return

        try:
            r = await account.client.post(
                "https://discord.com/api/v9/unique-username/registration-check",
                json={"username": username},
                timeout=10
            )

            if r.status_code == 200:
                if r.json().get("taken") is False:
                    logging.info(f"[AVAILABLE] {username}")
                    await notify_available(username)
                else:
                    logging.info(f"[TAKEN] {username}")

            elif r.status_code == 429:
                retry = r.json().get("retry_after", 10)
                account.next_retry = datetime.now() + timedelta(seconds=retry + 5)
                logging.warning(f"⏳ Rate limited: waiting {retry + 5}s")
                await self.queue.put(username)

            else:
                await self.queue.put(username)

        except Exception as e:
            logging.error(f"❌ Error checking {username}: {str(e)}")
            await self.queue.put(username)

    async def worker(self):
        while True:
            username = await self.queue.get()
            await self.check(username)
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            self.queue.task_done()

    async def run(self):
        asyncio.create_task(self.producer())
        asyncio.create_task(self.worker())
        while True:
            await asyncio.sleep(10)

# ====== FASTAPI WEB SERVICE ======
app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "ok"}

# ====== START SCANNER + RUN SERVER ======
async def main():
    scanner = DiscordScanner(TOKEN)
    asyncio.create_task(scanner.run())
    port = int(os.getenv("PORT", 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
