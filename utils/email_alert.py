import smtplib
from email.message import EmailMessage
import ssl

def send_email_alert(subject, body, image_bytes, to_email, config):
    """
    Envía una alerta por correo electrónico con una imagen adjunta.
    
    Parámetros:
    - subject: Asunto del correo.
    - body: Texto plano del mensaje.
    - image_bytes: contenido JPEG en binario.
    - to_email: destinatario.
    - config: diccionario con claves:
        - EMAIL_FROM
        - EMAIL_PASSWORD
        - EMAIL_SERVER
        - EMAIL_PORT
    """
    try:
        msg = EmailMessage()
        msg["From"] = config["EMAIL_FROM"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Adjuntar imagen JPEG como "alerta.jpg"
        msg.add_attachment(image_bytes, maintype="image", subtype="jpeg", filename="alerta.jpg")

        # Conexión segura SSL
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config["EMAIL_SERVER"], config["EMAIL_PORT"], context=context) as server:
            server.login(config["EMAIL_FROM"], config["EMAIL_PASSWORD"])
            server.send_message(msg)

        print(f"[Email] Alerta enviada a {to_email}")

    except Exception as e:
        print(f"[Email] Error al enviar alerta: {e}")
