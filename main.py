def start_sniping():
    time.sleep(15)
    print("🚀 الصيد بدأ الآن...")

    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL غير موجود")
        return

    # رسالة اختبار
    test = requests.post(
        WEBHOOK_URL,
        json={"content": "✅ Ultra Sniper شغال الآن"},
        timeout=10
    )
    print("Webhook test:", test.status_code, test.text)

    while True:
        target = ''.join(random.choice(string.ascii_lowercase) for _ in range(3)) + random.choice("._0123456789")

        headers = {"Authorization": TOKEN}
        url = f"https://discord.com/api/v9/users/search?query={target}"

        try:
            res = requests.get(url, headers=headers, timeout=10)

            if res.status_code == 200:
                users = res.json().get("users", [])
                if not any(u.get("username","").lower() == target.lower() for u in users):
                    content = f"🎯 صيد محتمل: `{target}`"
                    if MY_ID:
                        content = f"<@{MY_ID}> " + content

                    hit = requests.post(
                        WEBHOOK_URL,
                        json={"content": content, "username": "Ultra Sniper"},
                        timeout=10
                    )
                    print("HIT:", target, hit.status_code)

            elif res.status_code == 429:
                time.sleep(60)

            elif res.status_code == 401:
                print("❌ التوكن غير صالح")
                return

        except Exception as e:
            print("Error:", e)

        time.sleep(25)
