import os
import time
import json
from utils.email_alert import send_email_alert

CONFIG_PATH = os.path.join("config", "notifications.json")
_last_email_time = 0  # Variable global (solo en memoria durante ejecución)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {
            "email_enabled": False,
            "email_to": "",
            "cooldown_seconds": 60
        }
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def send_notification_if_gesture(image_path):
    global _last_email_time
    config = load_config()

    if not config.get("email_enabled", False):
        print("[Notificaciones] Notificaciones por correo desactivadas.")
        return

    cooldown = config.get("cooldown_seconds", 60)
    now = time.time()
    if now - _last_email_time < cooldown:
        print(f"[Notificaciones] Cooldown activo ({cooldown}s). No se enviará correo.")
        return

    # Leer imagen guardada por IA en carpeta sessions/
    if not os.path.exists(image_path):
        print(f"[Notificaciones] Imagen no encontrada: {image_path}")
        return

    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
    except Exception as e:
        print(f"[Notificaciones] Error leyendo imagen: {e}")
        return

    subject = "🔔 Gesto detectado - PiVision IA"
    body = "Se ha detectado un gesto (ej. manos arriba). Imagen adjunta."

    email_config = {
        "EMAIL_SERVER": "smtp.gmail.com",
        "EMAIL_PORT": 465,
        "EMAIL_FROM": "pivision.alerts@gmail.com",  # correo saliente fijo
        "EMAIL_PASSWORD": "gkja ntyb gono aynv",  # contraseña de aplicación segura (NO editable por el usuario)
    }

    to_email = config.get("email_to", "").strip()
    if not to_email:
        print("[Notificaciones] No se ha configurado un correo de destino.")
        return

    send_email_alert(
        subject=subject,
        body=body,
        image_bytes=image_data,
        to_email=to_email,
        config=email_config
    )

    _last_email_time = now
