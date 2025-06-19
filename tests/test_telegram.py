from utils.telegram_alert import send_telegram_alert

# Credenciales del bot y destino
TOKEN = "7758206368:AAG77jBM8dLjLPfy14ZsOxeUBgdbAsQMYhU"
CHAT_ID = "7950367373"

# Mensaje de prueba y ruta de imagen de ejemplo
MENSAJE = "🔔 Prueba desde PiVision IA – Telegram funcionando correctamente"
IMAGEN = "sessions/Luis.jpg"  # Asegúrate que exista

# Envío
send_telegram_alert(TOKEN, CHAT_ID, MENSAJE, IMAGEN)
