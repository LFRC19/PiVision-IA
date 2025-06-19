# PiVision IA 🎥🧠

Sistema de detección de rostros basado en inteligencia artificial, diseñado para ejecutarse de forma completamente headless en una Raspberry Pi con **Raspberry Pi OS Lite**. Ideal como nuestro proyecto de residencia profesional, solución de videovigilancia, o base para sistemas de visión artificial embebidos.

---

## 📌 Características actuales

* ✅ Detección en tiempo real de rostros desde consola (sin GUI)
* ✅ Detección automática de cámaras conectadas (`/dev/videoX`)
* ✅ Gestión de múltiples streams simultáneos
* ✅ Configuración de resolución y FPS desde CLI (`--width`, `--height`, `--fps`)
* ✅ Buffer circular en memoria
* ✅ Detección de movimiento (`cv2.absdiff`)
* ✅ Preprocesamiento (blur, grises)
* ✅ Logging en archivo (`log/eventos.log`) y consola
* ✅ Detección facial con MediaPipe + modelo Caffe
* ✅ Face Mesh para extracción de landmarks
* ✅ Normalización de rostros (alineación, crop, resize)
* ✅ Control de duplicados por firma facial
* ✅ Reconocimiento facial en tiempo real con MobileFaceNet (TFLite)
* ✅ Registro CLI de rostros conocidos en base SQLite
* ✅ Matching facial con umbral configurable
* ✅ Captura y logging con cooldown
* ✅ Organización de capturas por sesiones
* ✅ **Servidor Flask** con MJPEG streaming (`/video_feed/<cam_id>`)
* ✅ **Dashboard DVR** accesible desde navegador
* ✅ **Notificaciones por correo y Telegram**
* ✅ **Panel web de configuración de alertas**
* ✅ **API REST**:  
  - `GET /api/v1/cameras` (lista las cámaras activas)  
  - `GET /api/v1/events` (obtiene eventos recientes)

---

## 🧠 Arquitectura del Proyecto

PiVision-IA/
├── app/
│   ├── __init__.py
│   ├── ai_engine.py
│   ├── camera_manager.py
│   ├── multi_camera_manager.py
│   ├── face_detector.py
│   ├── face_mesh_processor.py
│   ├── face_normalizer.py
│   ├── face_signature.py
│   ├── frame_processor.py
│   ├── gesture_handler.py
│   ├── system_monitor.py
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── auth.py
│   │   └── api.py
│   └── templates/
│       ├── index.html
│       └── notifications.html
├── config/
│   ├── settings.py
│   └── notifications.json
├── database/
│   └── pivision.db
├── models/
│   ├── deploy.prototxt
│   ├── res10_300x300_ssd_iter_140000_fp16.caffemodel
│   └── mobilefacenet.tflite
├── utils/
│   ├── email_alert.py
│   └── telegram_alert.py
├── tests/
│   ├── test_email.py
│   └── test_telegram.py
├── vision.py
├── register_face.py
├── init_db.py
├── db.py
├── face_encoder.py
│   ├── face_matcher.py
│   └── notifier.py
├── static/
├── log/
│   └── eventos.log
├── rostros/
├── sessions/
├── .gitignore
├── requirements.txt
└── README.md

---

## ⚙️ Dependencias

```bash
sudo apt install python3-opencv
pip install tflite-runtime mediapipe numpy opencv-python-headless flask psutil
```

- **tflite-runtime**: Modelo MobileFaceNet
- **mediapipe**: Face detection, Face Mesh, Holistic
- **opencv-python-headless**: Procesamiento de video
- **flask**: Servidor web y dashboard
- **psutil**: Métricas CPU/RAM/disco
- **numpy**: Cálculos vectoriales

---

## 🧠 Reconocimiento Facial

- MobileFaceNet en TFLite (`models/mobilefacenet.tflite`)
- `face_encoder.py` para extracción de vectores
- `face_matcher.py` para matching con umbral
- Registro manual con `register_face.py`
- Base de datos `pivision.db` con:
  - Tabla `users`
  - Tabla `known_faces`
  - Tabla `detection_events`

---

## 🔔 Sistema de Notificaciones

- 📧 Envío de correos desde `pivision.alerts@gmail.com`
- 💬 Envío de mensajes por Telegram (requiere Bot + chat_id)
- 🧠 Solo se activa ante **gestos detectados**
- 🕐 Cooldown mínimo de 60s por seguridad
- 🌐 Configurable desde el panel web `/dashboard/notifications`

---

## 🔐 Gestión de Usuarios

- Login con contraseña protegida
- Sesiones vía `Flask.session`
- Decoradores `@login_required`
- Nombre del usuario visible
- Logout con botón moderno
- Cámaras operan incluso tras cerrar sesión

---

## 🧪 Estado Funcional Actual

- `python3 -m app.vision --nogui` para correr sin interfaz
- Web accesible vía navegador en `/`
- Dashboard con stream, métricas, historial, y cards
- Eventos SSE en tiempo real
- Captura organizada y logging completo

---

## 🚀 Próximas Fases

1. 🧪 Testing con `pytest`
2. 🔄 Service con `systemd`
3. 📚 Documentación final
4. ☁️ Hosting remoto / visualización externa
5. 🧠 Mejora de modelos (detección, embeddings, tracking)

---

## 🔒 Licencia

MIT License — libre para uso, modificación y distribución.

---

## ✍️ Autores

**Luis Fernando Rodriguez Cruz & Nayeli Ortiz Garcia**  
Desarrollado 100% sin entorno gráfico en Raspberry Pi (headless SSH).
