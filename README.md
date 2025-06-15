# PiVision IA 🎥🧠

Sistema de detección de rostros basado en inteligencia artificial, diseñado para ejecutarse de forma completamente headless en una Raspberry Pi con **Raspberry Pi OS Lite**. Ideal como nuestro proyecto de residencia profesional, solución de videovigilancia, o base para sistemas de visión artificial embebidos.

---

## 📌 Características actuales

* ✅ Detección en tiempo real de rostros desde consola (sin GUI).
* ✅ Detección automática de cámaras conectadas (`/dev/videoX`).
* ✅ Gestión de múltiples streams simultáneos.
* ✅ Configuración de resolución y FPS desde línea de comandos (`--width`, `--height`, `--fps`).
* ✅ Buffer circular para almacenar los últimos frames en memoria.
* ✅ Detección de movimiento mediante diferencia de frames (`cv2.absdiff`).
* ✅ Preprocesamiento con desenfoque y escala de grises (`cv2.GaussianBlur`, `cv2.cvtColor`).
* ✅ Logging estructurado en archivo (`log/eventos.log`) y salida moderada por consola.
* ✅ Pipeline de detección facial con **MediaPipe face_detection** paralelo al modelo Caffe.
* ✅ Extracción de landmarks faciales en tiempo real con **MediaPipe Face Mesh**.
* ✅ Normalización de rostros (alineación, recorte, resize).
* ✅ Control de duplicados: guarda rostro solo si es distinto (firma facial por landmarks).
* ✅ Reconocimiento facial en tiempo real con **MobileFaceNet (TFLite)**.
* ✅ Registro de rostros conocidos en base de datos vía script.
* ✅ Matching con umbral de confianza y detección de rostros desconocidos.
* ✅ Captura y logging con control de frecuencia (`cooldown`) por rostro.
* ✅ Organización de sesiones de captura con timestamp automático.
* ✅ **Servidor Flask con MJPEG streaming web** desde `/video_feed/<cam_id>` o `/snapshot/<cam_id>`.
* ✅ **Panel web DVR** con grid de cámaras funcionando desde navegador.

---

## 🧠 Arquitectura del Proyecto

```plaintext
PiVision-IA/
├── app/
│   ├── __init__.py
│   ├── camera_manager.py
│   ├── multi_camera_manager.py
│   ├── frame_processor.py
│   ├── face_detector.py
│   ├── face_mesh_processor.py
│   ├── face_normalizer.py
│   ├── face_signature.py
│   ├── routes/
│   │   └── dashboard.py         # Streaming MJPEG + snapshot + métricas
│   └── vision.py                # Script principal headless con IA integrada
├── config/
│   └── settings.py              # Configuración de cámara y paths
├── database/
│   └── pivision.db              # Base de datos SQLite (excluida por .gitignore)
├── models/
│   ├── deploy.prototxt
│   ├── res10_300x300_ssd_iter_140000_fp16.caffemodel
│   └── mobilefacenet.tflite     # Modelo TFLite para reconocimiento facial
├── log/
│   └── eventos.log
├── rostros/
├── static/
├── templates/
│   └── index.html               # Grid visual en el navegador
├── tests/
├── register_face.py            # Script CLI para registrar nuevos rostros conocidos
├── init_db.py                  # Inicializa base de datos pivision.db
├── db.py                       # Acceso a base de datos
├── face_encoder.py             # Codificación facial con TFLite
├── face_matcher.py             # Comparación de rostros con base
├── reset_cam.sh
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Dependencias

Instaladas vía `apt` y `pip` en un entorno `venv` con `--system-site-packages`:

```bash
sudo apt install python3-opencv
pip install tflite-runtime mediapipe numpy opencv-python-headless flask psutil
```

Dependencias clave:

- `tflite-runtime`: ejecución del modelo MobileFaceNet sin instalar TensorFlow completo.
- `mediapipe`: detección facial + landmarks.
- `opencv-python-headless`: procesamiento de video y rostros.
- `flask`: servidor web para streaming.
- `psutil`: métricas del sistema (CPU, RAM, disco).
- `numpy`: manipulación de vectores y distancias.

---

## 🧠 Sistema de Reconocimiento Facial (Fase 4.1)

Desde junio 2025, el sistema cuenta con reconocimiento facial completo basado en aprendizaje profundo y sin GUI. Incluye:

- ✅ Modelo MobileFaceNet (`mobilefacenet.tflite`) para generación de vectores faciales.
- ✅ Codificador `face_encoder.py` con normalización y salida de embeddings.
- ✅ Comparador `face_matcher.py` con umbral de distancia euclidiana.
- ✅ Script de registro de rostros (`register_face.py`) desde consola.
- ✅ Identificación en tiempo real desde consola (modo headless).
- ✅ Base de datos SQLite (`pivision.db`) con tablas `users`, `known_faces`, `detection_events`.
- ✅ Logging en `eventos.log` y en base de datos por cada detección.
- ✅ Guardado organizado en `rostros/` por sesión.
- ✅ Control de frecuencia (`cooldown`) para evitar spam y duplicados.

---

## 🧪 Estado funcional actual

* `vision.py` ejecutable como módulo: `python3 -m app.vision --nogui`.
* Soporte multi-cámara, detección de movimiento y reconocimiento facial.
* Logging de todos los eventos relevantes.
* Exportación controlada de rostros detectados.
* Registro por consola de identificaciones recientes.
* ✅ Stream MJPEG desde navegador (`/video_feed/0`) vía Flask.
* ✅ Snapshot en `/snapshot/0` para debug o monitoreo puntual.
* ✅ Página web (`/`) con grid visual del stream.

---

## 🚀 Próximas metas

1. 🧠 **Integración de lógica IA en el streaming** (detección, overlays, eventos SSE).
2. 🌐 **API REST** con JSON de eventos.
3. 🧪 **Pruebas unitarias** con `pytest`.
4. 🔄 **Servicios `systemd`** para arranque automático.
5. 📝 **Documentación** técnica y manual de usuario.
6. ☁️ **Repositorio GitHub** como respaldo de prácticas profesionales.

---

## 🔒 Licencia

MIT License — libre para uso, modificación y distribución.

---

## ✍️ Autores

**Luis Fernando Rodriguez Cruz & Nayeli Ortiz Garcia**  
Desarrollado en una Raspberry Pi sin entorno gráfico, accediendo vía SSH desde Visual Studio Code.
