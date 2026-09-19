import requests
import time
import os

TOKEN = os.environ.get("1641879499:_lP6SnzTPGs45k1mDKFkqkrEwG6BhASRrxk")

URL = f"https://tapi.bale.ai/bot{TOKEN}/"

offset = 0

print("🤖 بات ابری بله اجرا شد!")

while True:
    try:
        response = requests.get(
            URL + "getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=40
        )

        data = response.json()

        for update in data.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message")
            if not message:
                continue

            chat_id = message["chat"]["id"]

            requests.post(
                URL + "sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "☁️ بات ابری من فعاله!"
                },
                timeout=15
            )

    except Exception as e:
        print("خطا:", e)
        time.sleep(5)
