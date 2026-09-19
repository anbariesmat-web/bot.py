import os
import time
import requests

TOKEN = os.getenv("1641879499:_lP6SnzTPGs45k1mDKFkqkrEwG6BhASRrxk")

if not TOKEN:
    raise RuntimeError("TOKEN environment variable is not set")

BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

# کاربران منتظر برای پیدا شدن یک نفر
waiting_user = None

# جفت‌های فعلی
partners = {}


def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=30
        )
        return response.json()
    except Exception as e:
        print("Send error:", e)
        return None


def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"

    data = {
        "timeout": 30
    }

    if offset is not None:
        data["offset"] = offset

    try:
        response = requests.post(
            url,
            json=data,
            timeout=40
        )
        return response.json()
    except Exception as e:
        print("Get updates error:", e)
        return {"ok": False, "result": []}


def find_partner(user_id):
    global waiting_user

    # اگر خود کاربر در صف است
    if waiting_user == user_id:
        return None

    # اگر یک نفر منتظر است
    if waiting_user is not None:
        partner = waiting_user
        waiting_user = None

        partners[user_id] = partner
        partners[partner] = user_id

        return partner

    # کسی منتظر نیست
    waiting_user = user_id
    return None


def remove_from_chat(user_id):
    global waiting_user

    if waiting_user == user_id:
        waiting_user = None

    partner = partners.pop(user_id, None)

    if partner is not None:
        partners.pop(partner, None)
        return partner

    return None


def handle_message(message):
    global waiting_user

    chat = message.get("chat", {})
    user_id = chat.get("id")
    text = message.get("text", "")

    if not user_id:
        return

    text = text.strip()

    # شروع
    if text == "/start":
        send_message(
            user_id,
            "سلام 👋\n"
            "به چت ناشناس خوش آمدی.\n\n"
            "برای پیدا کردن یک نفر ناشناس، /find را بفرست.\n"
            "برای پایان گفتگو، /stop را بفرست."
        )
        return

    # پیدا کردن نفر
    if text == "/find":
        if user_id in partners:
            send_message(
                user_id,
                "تو الان در یک گفتگوی ناشناس هستی.\n"
                "برای پایان دادن /stop را بفرست."
            )
            return

        partner = find_partner(user_id)

        if partner is None:
            send_message(
                user_id,
                "⏳ در حال پیدا کردن یک نفر برای چت هستم..."
            )
        else:
            send_message(
                user_id,
                "✅ یک نفر پیدا شد!\n"
                "هر پیامی بفرستی، ناشناس برای او ارسال می‌شود."
            )

            send_message(
                partner,
                "✅ یک نفر پیدا شد!\n"
                "هر پیامی بفرستی، ناشناس برای او ارسال می‌شود."
            )

        return

    # پایان گفتگو
    if text == "/stop":
        partner = remove_from_chat(user_id)

        if partner is not None:
            send_message(
                user_id,
                "🛑 گفتگو تمام شد."
            )
            send_message(
                partner,
                "🛑 طرف مقابل گفتگو را تمام کرد."
            )
        else:
            send_message(
                user_id,
                "شما در حال حاضر در گفتگویی نیستید."
            )

        return

    # ارسال پیام ناشناس
    if user_id in partners:
        partner = partners[user_id]

        send_message(
            partner,
            "💬 پیام ناشناس:\n\n" + text
        )

        return

    send_message(
        user_id,
        "ابتدا /find را بفرست تا یک نفر برای چت پیدا شود."
    )


def main():
    print("Bale anonymous chat bot started.")

    offset = None

    while True:
        try:
            data = get_updates(offset)

            if not data.get("ok"):
                time.sleep(3)
                continue

            updates = data.get("result", [])

            for update in updates:
                offset = update.get("update_id", 0) + 1

                message = update.get("message")

                if message:
                    handle_message(message)

        except Exception as e:
            print("Main error:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
