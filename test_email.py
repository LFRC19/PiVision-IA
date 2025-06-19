from utils.email_alert import send_email_alert
import config.settings as settings
import os

def main():
    image_path = os.path.join("rostros", "Luis.jpg")

    try:
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()
    except FileNotFoundError:
        print(f"[Error] No se encontró la imagen en {image_path}")
        return

    config = {
        "EMAIL_SERVER": settings.EMAIL_SERVER,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_FROM": settings.EMAIL_FROM,
        "EMAIL_PASSWORD": settings.EMAIL_PASSWORD,
    }

    send_email_alert(
        subject="🔔 Alerta: Detección de rostro - PiVision IA",
        body="Se ha detectado el rostro 'Luis' en la zona vigilada.",
        image_bytes=image_data,
        to_email=settings.EMAIL_TO,
        config=config
    )

if __name__ == "__main__":
    main()
