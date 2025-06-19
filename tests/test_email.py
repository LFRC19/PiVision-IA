from utils.email_alert import send_email_alert
import config.settings as settings

def main():
    # Leer una imagen desde disco para enviar (usa una existente en tu proyecto)
    with open("static/snapshot.jpg", "rb") as img_file:
        image_data = img_file.read()

    # Construir el diccionario de configuración
    config = {
        "EMAIL_SERVER": settings.EMAIL_SERVER,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_FROM": settings.EMAIL_FROM,
        "EMAIL_PASSWORD": settings.EMAIL_PASSWORD,
    }

    # Enviar alerta de prueba
    send_email_alert(
        subject="🔔 Alerta de prueba PiVision IA",
        body="Esta es una prueba de envío de correos desde el sistema de vigilancia.",
        image_bytes=image_data,
        to_email=settings.EMAIL_TO,
        config=config
    )

if __name__ == "__main__":
    main()
