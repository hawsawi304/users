import os, random, time, requests, threading, datetime
from flask import Flask

app = Flask(__name__)

stats = {
    "checked": 0,
    "found": 0,
    "current": "Starting...",
    "msg_id": None,
    "status": "متصل ✅"
}

@app.route("/")
def home():
    return f"V7.2 ACTIVE - CHECKED: {stats['checked']}"

def update_status(webhook):
    while True:
        try:
            payload = {
                "embeds": [{
                    "title": "📡 رادار القنص V7.2 - المطور",
                    "description": f"🔍 يفحص الآن: `{stats['current']}`\n🚦 الحالة: `{stats['status']}`",
                    "color": 0x3498db,
                    "fields": [
                        {"name": "📊 فحص حقيقي", "value": f"`{stats['checked']}`", "inline": True},
                        {"name": "🎯 تم صيد", "value": f"`{stats['found']}`", "inline": True}
                    ],
                    "footer": {"text": "Render Auto-Check System"},
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }]
            }
            if stats["msg_id"] is None:
                r = requests.post(webhook + "?wait=true", json=payload, timeout=10)
                if r.status_code == 200:
                    stats["msg_id"] = r.json().get("id")
            else:
                requests.patch(f"{webhook}/messages/{stats['msg_id']}", json=payload, timeout=10)
        except:
            pass
        time.sleep(15)

def check_username(user, headers):
    try:
        r = requests.post(
            "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
            json={"username": user},
            headers=headers,
            timeout=5
        )
        if r.status_code == 200:
            stats["status"] = "متصل ✅"
            return "available" if r.json().get("taken") is False else "taken"
        elif r.status_code == 429:
            stats["status"] = "محظور مؤقتاً ⚠️"
            return "rate_limit"
        return "error"
    except:
        return "error"

def generate_username():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789._"
    return "".join(random.choices(chars, k=4))

def sniper():
    webhook = os.getenv("WEBHOOK_URL")
    if not webhook: return

    threading.Thread(target=update_status, args=(webhook,), daemon=True).start()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    while True:
        try:
            user = generate_username()
            stats["current"] = user

            res = check_username(user, headers)
            
            if res == "available":
                # تأكيد مزدوج سريع
                time.sleep(0.5)
                if check_username(user, headers) == "available":
                    stats["found"] += 1
                    requests.post(webhook, json={"content": f"🎯 **يوزر متاح مؤكد:** `{user}`"}, timeout=10)
                stats["checked"] += 1
            elif res == "taken":
                stats["checked"] += 1
            elif res == "rate_limit":
                time.sleep(40) # انتظار أطول لفك الحظر

            time.sleep(1.2) # سرعة متزنة

        except:
            stats["status"] = "مشكلة اتصال 🌐"
            time.sleep(10)

started = False

@app.before_request
def start_sniper_once():
    global started
    if not started:
        started = True
        threading.Thread(target=sniper, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
