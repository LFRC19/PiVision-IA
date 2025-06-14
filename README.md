# PiVision IA 🎥🤖

Sistema de detección de rostros basado en inteligencia artificial, diseñado para ejecutarse de forma completamente headless en una Raspberry Pi con **Raspberry Pi OS Lite**. Ideal como proyecto de residencia profesional, solución de videovigilancia, o base para sistemas de visión artificial embebidos.

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
* ✅ Pipeline de detección facial con **MediaPipe face\_detection** paralelo al modelo Caffe.
* ✅ Extracción de landmarks faciales en tiempo real con **MediaPipe Face Mesh**.
* ✅ Normalización de rostros (alineación, recorte, resize).
* ✅ Control de duplicados: guarda rostro solo si es distinto (firma facial por landmarks).

---

## 🧠 Arquitectura del Proyecto

```plaintext
PiVision-IA/
├── app/
│   ├── camera_manager.py        # Clase CameraManager con detección, buffer y control de parámetros
│   ├── multi_camera_manager.py  # Clase MultiCameraManager para gestionar múltiples cámaras simultáneas
│   ├── frame_processor.py       # Procesamiento básico: movimiento, filtros, escala de grises
│   ├── face_detector.py         # MediaPipe face_detection: detección facial en tiempo real
│   ├── face_mesh_processor.py   # MediaPipe face_mesh: extracción de landmarks
│   ├── face_normalizer.py       # Alineación y recorte de rostro a partir de landmarks
│   ├── face_signature.py        # Firma facial basada en landmarks clave para evitar duplicados
│   └── vision.py                # Script principal de detección headless con integración completa
├── models/
│   ├── deploy.prototxt          # Configuración de red neuronal (Caffe)
│   └── res10_300x300_ssd_iter_140000_fp16.caffemodel
├── static/                      # Recursos web (Flask)
├── templates/                   # Vistas HTML (Flask)
├── tests/                       # Pruebas unitarias (en desarrollo)
├── reset_cam.sh                 # Script para liberar /dev/video0
├── log/                         # Carpeta para registros de eventos
│   └── eventos.log              # Archivo dinámico de logs (excluido por .gitignore)
├── rostros/                     # Carpeta de salida para rostros normalizados
├── requirements.txt             # Dependencias del proyecto
├── .gitignore                   # Archivos excluidos del repo
└── README.md                    # Documentación del proyecto
```

---

## ⚙️ Dependencias

Instaladas vía `apt` y `pip` en un entorno `venv` con `--system-site-packages`:

```bash
sudo apt install python3-opencv
pip install flask django mysql-connector-python mediapipe numpy matplotlib pandas
```

MediaPipe y NumPy son utilizadas para procesamiento facial, landmarks y comparación de firmas.

---

## 🧪 Estado funcional actual

* **Detección de rostros**: `vision.py` ejecutable como módulo (`python3 -m app.vision`).
* **Parámetros de cámara**: Ajustables con flags.
* **Buffer circular**: Guarda hasta 100 frames.
* **Multi-cámara**: Gestiona varias cámaras simultáneamente con `MultiCameraManager`.
* **Detección de movimiento**: basada en diferencia de frames y contornos.
* **Preprocesamiento**: escala de grises + filtros de ruido.
* **Logging**: todos los eventos registrados con timestamp en archivo y moderados por consola.
* **MediaPipe**: detección facial y landmarks con `face_detection` y `face_mesh`.
* **Normalización**: recorte y alineación de rostros detectados.
* **Deduplicación**: solo se guardan rostros distintos según firma facial generada.

---

## 🚀 Próximas metas

1. 🌐 **Servidor Flask**: Streaming MJPEG y API REST para métricas.
2. 🧪 **Pruebas unitarias** con `pytest`.
3. 🔄 **Servicios `systemd`** para arranque automático.
4. 📝 **Documentación** técnica y manual de usuario.
5. ☁️ **Repositorio GitHub** como respaldo de prácticas profesionales.

---

## 🔒 Licencia

MIT License — libre para uso, modificación y distribución.

---

## ✍️ Autores

**Luis Fernando Rodriguez Cruz & Nayeli Ortiz Garcia**
Desarrollado en una Raspberry Pi sin entorno gráfico, accediendo vía SSH desde Visual Studio Code.
