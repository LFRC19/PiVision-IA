
# PiVision IA 🎥🧠

Sistema de vigilancia inteligente basado en reconocimiento facial, desarrollado para ejecutarse completamente sin entorno gráfico en una Raspberry Pi con Raspberry Pi OS Lite. Este proyecto forma parte de la **residencia profesional** de Ingeniería en Sistemas Computacionales.

---

## ✍️ Autores

Luis Fernando Rodriguez Cruz  
Nayeli Ortiz Garcia  
Desarrollado 100% sin entorno gráfico en Raspberry Pi (headless SSH)

---

## 📌 Características principales

* Detección de movimiento con OpenCV
* Detección y reconocimiento facial en tiempo real
* Preprocesamiento facial: alineación, recorte, normalización
* Reconocimiento con MobileFaceNet en TensorFlow Lite
* Logging de eventos en consola, archivo y base de datos SQLite
* Registro y gestión de rostros conocidos
* Captura y almacenamiento de imágenes por sesión
* Detección de gestos con MediaPipe Holistic
* Contador de personas únicas por cámara
* Streaming en vivo MJPEG vía Flask
* Dashboard web tipo DVR accesible desde red local o internet
* Panel de configuración web para notificaciones
* Notificaciones automáticas por correo y/o Telegram ante gestos
* API REST para acceso remoto a cámaras y eventos
* Autenticación de usuarios (login/logout)
* Acceso remoto global mediante Ngrok

---

## 🧠 Arquitectura del Proyecto

```
PiVision-IA/
├── app/
│   ├── ai_engine.py
│   ├── camera_manager.py
│   ├── multi_camera_manager.py
│   ├── face_mesh_processor.py
│   ├── face_normalizer.py
│   ├── frame_processor.py
│   ├── gesture_handler.py
│   ├── system_monitor.py
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── api.py
│   │   └── auth.py
│   └── templates/
│       ├── index.html
│       └── notifications.html
├── database/
│   └── pivision.db
├── config/
│   ├── settings.py
│   └── notifications.json
├── models/ (modelos IA: Caffe + TFLite)
├── utils/ (correo y Telegram)
├── log/ (eventos)
├── sessions/ (capturas)
├── vision.py
├── server.py
├── register_face.py
├── init_db.py
├── db.py
├── face_encoder.py
├── requirements.txt
├── .env.example
└── README.txt
```

---

## ⚙️ Requisitos e instalación

```bash
sudo apt update
sudo apt install -y python3-opencv v4l-utils
pip install -r requirements.txt
pip install python-dotenv
```

Archivo `requirements.txt` mínimo:

```
flask
mediapipe
numpy
opencv-python-headless
psutil
python-dotenv
tflite-runtime
```

---

## ⚙️ Configuración inicial

### 1. Crear archivo `.env`:

```dotenv
USE_TPU=false
FACE_MATCH_THRESHOLD=0.45
GESTURE_DETECTION_CONFIDENCE=0.7
DETECTION_FRAME_SKIP=2
```

### 2. Configurar cámaras en `config/settings.py`:

```python
CAMERA_IDS = [0, 2]  # cámaras activas
```

### 3. Configurar notificaciones:

Desde el navegador: `/dashboard/notifications`

Permite definir destinatario, método (correo o Telegram), y tiempo de espera entre alertas.

---

## 🚀 Ejecución del sistema

```bash
source venv/bin/activate
cp .env.example .env
nano .env  # editar umbrales IA
nano config/settings.py  # configurar cámaras

python server.py
```

Accede desde navegador local:  
`http://<IP_del_Pi>:5000/`

---

## 🌍 Acceso remoto (Ngrok)

### Instalación (solo una vez):

```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.zip
unzip ngrok-v3-stable-linux-arm.zip
sudo mv ngrok /usr/local/bin
ngrok config add-authtoken TU_TOKEN
```

### Uso:

```bash
ngrok http 5000
```

Copia la URL HTTPS pública que aparece para acceder al dashboard desde cualquier red.

---

## 🧪 Medición de rendimiento

Muestra en consola:

```
[DEBUG] Tiempo de inferencia facial: 0.113 s
```

Se puede comparar rendimiento CPU vs TPU (`USE_TPU=true`)  
y ajustar `DETECTION_FRAME_SKIP` para mejorar FPS.

---

## 📁 Registro y Evidencia

Todos los eventos quedan registrados en:

* `log/eventos.log`: eventos generales
* `sessions/`: imágenes organizadas por fecha y persona
* `database/pivision.db`: base de datos SQLite
* `dashboard`: historial visual desde navegador

---

## 🛠️ Automatización recomendada (fase 8)

Para automatizar el inicio al arrancar la Raspberry Pi:

**1. Crear servicio systemd para Flask**  
**2. Crear servicio systemd para Ngrok**

Ambos deben lanzarse en background, asegurando el acceso constante desde internet.

## ⚙️ Automatización de arranque (Ngrok + servidor Flask)

### 1. Crear servicio systemd para Flask (server.py)

```bash
sudo nano /etc/systemd/system/pivision.service
```

Contenido sugerido:

```
[Unit]
Description=PiVision IA Flask Server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/PiVision-IA
ExecStart=/home/pi/PiVision-IA/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego habilitarlo:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable pivision
sudo systemctl start pivision
```

---

### 2. Crear servicio systemd para Ngrok

```bash
sudo nano /etc/systemd/system/ngrok.service
```

Contenido:

```
[Unit]
Description=Ngrok Tunnel for Flask
After=network.target

[Service]
ExecStart=/usr/local/bin/ngrok http 5000
Restart=on-failure
User=pi
WorkingDirectory=/home/pi

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl enable ngrok
sudo systemctl start ngrok
```

---

Ambos servicios se iniciarán automáticamente al prender la Raspberry Pi. Asegúrse de que el entorno virtual esté correctamente configurado en el servicio de Flask.

*(Estos pasos se integrarán como parte de la documentación final.)*

---

## 🔒 Licencia

MIT License


---

