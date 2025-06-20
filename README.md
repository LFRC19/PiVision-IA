# PiVision IA 🎥🧠

Sistema de detección de rostros basado en inteligencia artificial, diseñado para ejecutarse de forma completamente headless en una Raspberry Pi con **Raspberry Pi OS Lite**. Ideal como proyecto de residencia profesional, solución de videovigilancia o base para sistemas de visión artificial embebidos.

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
* ✅ **Servidor Flask** con MJPEG streaming (`/dashboard/video_feed/<cam_id>`)
* ✅ **Dashboard DVR** accesible desde navegador
* ✅ **Notificaciones por correo y Telegram** (sólo ante gestos)
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
│   ├── frame_processor.py  
│   ├── face_mesh_processor.py  
│   ├── face_normalizer.py  
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
├── sessions/  
├── .env.example  
├── config/settings.py  
├── requirements.txt  
└── README.txt

---

## ⚙️ Dependencias

```bash
sudo apt update
sudo apt install -y python3-opencv v4l-utils
pip install -r requirements.txt
pip install python-dotenv
```

**requirements.txt** debe incluir:
```
flask
tflite-runtime
mediapipe
numpy
opencv-python-headless
psutil
python-dotenv
```

---

## ⚙️ Configuración

1. **`.env`** (a crear en la raíz):
   ```dotenv
   # --- Acelerador TPU (Edge TPU / Hailo) ---
   USE_TPU=false

   # --- Parámetros IA dinámicos ---
   FACE_MATCH_THRESHOLD=0.45
   GESTURE_DETECTION_CONFIDENCE=0.7
   DETECTION_FRAME_SKIP=2
   ```

2. **Cámaras**: ajusta `config/settings.py` según índices válidos:
   ```python
   CAMERA_IDS = [0, 2]  # según v4l2-ctl --list-devices
   ```

3. **Notificaciones**:
   - Panel web: `/dashboard/notifications`
   - Configura email y Telegram, con cooldown configurable.

---

## 🏁 Uso

```bash
# Activar .env
cp .env.example .env
# Edita .env y settings.py
python server.py
```

Abre en tu navegador: `http://<IP_de_tu_Pi>:5000/`

---

## 🧪 Medición de rendimiento

- En consola ves:
  ```
  [DEBUG] Tiempo de inferencia facial: 0.113 s
  ```
- Compara CPU vs TPU (al activar `USE_TPU=true`).
- Ajusta `DETECTION_FRAME_SKIP` para mejorar FPS.

---

## 📝 Contribuir y GitHub

```bash
git add .
git commit -m "chore: versión estable con multi-cámara, TPU, config dinámica"
git push origin main
```

---

## 🔒 Licencia

MIT License

