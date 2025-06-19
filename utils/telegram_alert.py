# telegram_alert.py
import requests
import os

def send_telegram_alert(token, chat_id, message, image_path=None):
    """
    Envía un mensaje (y opcionalmente una imagen) al chat_id especificado vía Telegram Bot API.
    """
    base_url = f"https://api.telegram.org/bot{token}"

    # 1. Enviar mensaje de texto
    try:
        requests.post(f"{base_url}/sendMessage", data={
            "chat_id": chat_id,
            "text": message
        })
    except Exception as e:
        print(f"[Telegram] ❌ Error enviando mensaje: {e}")

    # 2. Enviar imagen si se especifica
    if image_path and os.path.isfile(image_path):
        try:
            with open(image_path, "rb") as img:
                requests.post(f"{base_url}/sendPhoto", data={
                    "chat_id": chat_id
                }, files={
                    "photo": img
                })
        except Exception as e:
            print(f"[Telegram] ❌ Error enviando imagen: {e}")
    elif image_path:
        print(f"[Telegram] ⚠️ Imagen no encontrada: {image_path}")
