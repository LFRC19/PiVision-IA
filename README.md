# PiVision IA 🎥🤖

Sistema de detección de rostros basado en inteligencia artificial, diseñado para ejecutarse de forma completamente headless en una Raspberry Pi con **Raspberry Pi OS Lite**. Ideal como proyecto de residencia profesional, solución de videovigilancia, o base para sistemas de visión artificial embebidos.

---

## 📌 Características actuales

* ✅ Detección en tiempo real de rostros desde consola (sin GUI).
* ✅ Detección automática de cámaras conectadas (`/dev/videoX`).
* ✅ Configuración de resolución y FPS desde línea de comandos (`--width`, `--height`, `--fps`).
* ✅ Buffer circular para almacenar los últimos frames en memoria.

---

## 🧠 Arquitectura del Proyecto

```plaintext
PiVision-IA/
├── app/
│   ├── camera_manager.py        # Clase CameraManager con detección, buffer y control de parámetros
│   └── vision.py                # Script principal de detección headless con flags de cámara
├── models/
│   ├── deploy.prototxt          # Configuración de red neuronal
│   └── res10_300x300_ssd_iter_140000_fp16.caffemodel
├── static/                      # Recursos web (Flask)
├── templates/                   # Vistas HTML (Flask)
├── tests/                       # Pruebas unitarias (en desarrollo)
├── reset_cam.sh                 # Script para liberar /dev/video0
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

No se han agregado nuevas dependencias para la fase de captura de video múltiple.

---

## 🧪 Estado funcional actual

* **Detección de rostros**: Vision.py ejecutable como módulo (`python3 -m app.vision`).
* **Parámetros de cámara**: Ajustables con flags.
* **Buffer circular**: Guarda hasta 100 frames.

---

## 🚀 Próximas metas

1. 🤝 **Múltiples streams** simultáneos: Implementar `MultiCameraManager` para gestionar varias cámaras.
2. 🌐 **Servidor Flask**: Streaming MJPEG y API REST para métricas.
3. 🧪 **Pruebas unitarias** con `pytest`.
4. 🔄 **Servicios `systemd`** para arranque automático.
5. 📝 **Documentación** técnica y manual de usuario.
6. ☁️ **Repositorio GitHub** como respaldo de prácticas profesionales.

---

## 🔒 Licencia

MIT License — libre para uso, modificación y distribución.

---


## AUTORES
-----
Luis Fernando Rodriguez Cruz & Nayeli Ortiz Garcia
Desarrollado en una Raspberry Pi sin entorno gráfico, accediendo vía SSH desde Visual Studio Code.
