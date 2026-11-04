import os
import json
import base64
import hmac
import hashlib
import time
import requests

from urllib.parse import parse_qsl
from http.server import BaseHTTPRequestHandler


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")


def verify_telegram_data(init_data):
    if not BOT_TOKEN or not init_data:
        return None

    data = dict(parse_qsl(init_data))
    received_hash = data.pop("hash", None)

    if not received_hash:
        return None

    check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(data.items())
    )

    secret = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret,
        check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    auth_date = int(data.get("auth_date", 0))

    if time.time() - auth_date > 86400:
        return None

    return json.loads(data["user"])


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        self.send_json(200, {
            "status": "PayMobile API ishlayapti"
        })

    def do_POST(self):

        try:
            length = int(self.headers.get("Content-Length", 0))

            if length <= 0 or length > 4_000_000:
                return self.send_json(400, {
                    "error": "Fayl hajmi juda katta"
                })

            body = self.rfile.read(length)
            data = json.loads(body)

            user = verify_telegram_data(
                data.get("initData", "")
            )

            if not user:
                return self.send_json(401, {
                    "error": "Telegram tekshiruvidan o'tmadi"
                })

            if not ADMIN_ID or not BOT_TOKEN:
                return self.send_json(500, {
                    "error": "Server sozlamalari mavjud emas"
                })

            receipt = data.get("receipt", "")

            if "," not in receipt:
                return self.send_json(400, {
                    "error": "Chek rasmi topilmadi"
                })

            mime, encoded = receipt.split(",", 1)

            image_type = mime.split(";")[0].replace(
                "data:", ""
            )

            if image_type not in (
                "image/jpeg",
                "image/png",
                "image/webp"
            ):
                return self.send_json(400, {
                    "error": "Rasm formati noto'g'ri"
                })

            image = base64.b64decode(
                encoded,
                validate=True
            )

            if len(image) > 2_500_000:
                return self.send_json(400, {
                    "error": "Rasm 2.5 MB dan oshmasin"
                })

            caption = (
                "💎 <b>YANGI PAYMOBILE UC BUYURTMASI</b>\n\n"
                f"👤 Mijoz: {user.get('first_name', '')}\n"
                f"🆔 Telegram ID: {user['id']}\n"
                f"🎮 PUBG ID: {data.get('pubgId', '')}\n"
                f"🏷 Nickname: {data.get('nickname', '')}\n"
                f"💎 UC: {data.get('uc', '')}\n"
                f"💰 Narx: {data.get('price', '')} so'm\n\n"
                "🧾 To'lov cheki ilova qilindi."
            )

            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id": ADMIN_ID,
                    "caption": caption,
                    "parse_mode": "HTML"
                },
                files={
                    "photo": (
                        "receipt.jpg",
                        image,
                        image_type
                    )
                },
                timeout=20
            )

            response.raise_for_status()

            return self.send_json(200, {
                "success": True,
                "message": "Buyurtma yuborildi"
            })

        except Exception:
            return self.send_json(500, {
                "error": "Buyurtmani yuborishda xatolik"
            })
