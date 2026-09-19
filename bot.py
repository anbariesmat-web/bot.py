import time
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# فقط اینجا توکن باتت را وارد کن
TOKEN = "1641879499:_lP6SnzTPGs45k1mDKFkqkrEwG6BhASRrxk"

BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

waiting_user = None
partners = {}


# برای اینکه Render سرویس را خاموش نکند
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        pass


def start_server():
    port = 10000
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


def send_message(chat_id, text):
    try:
        requests.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=30
        )
    except Exception as e:
        print("Send error:", e)


def get_updates(offset=None):
    try:
        data = {"timeout": 30}

        if offset is not None:
            data["offset"] = offset

        response = requests.post(
            f"{BASE_URL}/getUpdates",
            json=data,
            timeout=40
        )

        return response.json()

    except Exception as e:
        print("Get updates error:", e)
        return {"ok": False, "result": []}


def find_partner(user_id):
    global waiting_user

    if waiting_user == user_id:
        return None

    if waiting_user is not None:
        partner = waiting_user

        waiting_user = None

        partners[user_id] = partner
        partners[partner] = user_id

        return partner

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

    chat = message.get("chat", {})
    user_id = chat.get("id")

    if not user_id:
        return

    text = message.get("text", "").strip()

    if text == "/start":

        send_message(
            user_id,
            "سلام 👋\n"
            "به چت ناشناس خوش آمدی.\n\n"
            "برای پیدا کردن یک نفر ناشناس:\n"
            "/find\n\n"
            "برای پایان گفتگو:\n"
            "/stop"
        )

        return

    if text == "/find":

        if user_id in partners:
            send_message(
                user_id,
                "تو الان در یک گفتگوی ناشناس هستی.\n"
                "برای پایان گفتگو /stop را بفرست."
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
                "پیامت به صورت ناشناس ارسال می‌شود."
            )

            send_message(
                partner,
                "✅ یک نفر پیدا شد!\n"
                "پیامت به صورت ناشناس ارسال می‌شود."
            )

        return

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


# اجرای سرور پورت
threading.Thread(
    target=start_server,
    daemon=True
).start()

# اجرای بات
main()
