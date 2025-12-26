import os
import asyncio
import httpx
import random
import string
import logging
from datetime import datetime
from fastapi import FastAPI
import uvicorn

# ====== ENV ======
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DELAY_MIN = float(os.getenv("DELAY_MIN", 3))
DELAY_MAX = float(os.getenv("DELAY_MAX", 6))

# ====== LOGGING ======
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ====== USERNAME GENERATOR ======
ALLOWED_CHARS = string.ascii_lowercase + string.digits + "._"

def generate_username():
    while True:
        length = random.randint(2, 4)
        username = "".join(random.choice(ALLOWED_CHARS) for _ in range(length))
        if username[0].isalnum() and username[-1].isalnum():
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
            logging.warning(f"⚠️ Webhook error {r.status_code}")

# ====== SCANNER ======
class DiscordScanner:
    def __init__(self, token):
        self.token = token.strip()
        self.client = httpx.AsyncClient(headers={"Authorization": self.token})
        self.rate_reset = datetime.now()

    async def check(self, username):
        if datetime.now() < self.rate_reset:
            await asyncio.sleep((self.rate_reset - datetime.now()).total_seconds())

        try:
            r = await self.client.post(
                "https://discord.com/api/v9/unique-username/registration-check",
                json={"username": username},
                timeout=10
            )
        except Exception as e:
            logging.error(f"❌ Network error for {username}: {e}")
            return

        # ★ التعامل مع 429 بشكل صحيح
        if r.status_code == 429:
            retry_after = None
            try:
                retry_after = float(r.json().get("retry_after", 0))
            except:
                retry_after = float(r.headers.get("Retry-After", 0))
            wait = retry_after + 3
            self.rate_reset = datetime.now() + timedelta(seconds=wait)
            logging.warning(f"⏳ Rate limited – waiting {wait}s")
            return

        # ✖️ رد غير صالح أو فارغ
        if not r.content:
            logging.warning(f"⚠️ Empty response for {username}")
            return

        # ✅ الرد صحيح
        try:
            data = r.json()
        except:
            logging.warning(f"⚠️ Response not JSON for {username}")
            return

        taken = data.get("taken")
        if taken is False:
            logging.info(f"[AVAILABLE] {username}")
            await notify_available(username)
        else:
            logging.info(f"[TAKEN] {username}")

    async def run(self):
        while True:
            name = generate_username()
            await self.check(name)
            await asyncio.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

# ====== FASTAPI ======
app = FastAPI()

@app.get("/ping")
async def ping():
    return {"status": "ok"}

async def main():
    scanner = DiscordScanner(TOKEN)
    asyncio.create_task(scanner.run())
    port = int(os.getenv("PORT", 10000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
