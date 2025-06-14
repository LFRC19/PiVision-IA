PiVision IA
===========

Sistema de detección de rostros basado en inteligencia artificial, diseñado para ejecutarse de forma completamente headless en una Raspberry Pi con Raspberry Pi OS Lite. Ideal como proyecto de residencia profesional, solución de videovigilancia, o base para sistemas de visión artificial embebidos.

CARACTERÍSTICAS ACTUALES
------------------------
- Detección en tiempo real de rostros desde consola (sin GUI).
- Uso de modelo DNN SSD con ResNet (formato Caffe).
- Acceso remoto vía SSH con Visual Studio Code.
- Proyecto modular con soporte para expansión web/API.
- Script auxiliar para desbloquear la cámara en caso de error.

ARQUITECTURA DEL PROYECTO
-------------------------
PiVision-IA/
├── app/
│   └── vision.py                  -> Script de detección principal (modo consola)
├── models/
│   ├── deploy.prototxt            -> Configuración de red neuronal
│   └── res10_300x300_ssd_iter_140000_fp16.caffemodel
├── static/                        -> Recursos web (Flask)
├── templates/                     -> Vistas HTML (Flask)
├── tests/                         -> Futuras pruebas unitarias
├── reset_cam.sh                   -> Script para liberar /dev/video0
├── run.py                         -> Entrada para servidor Flask (en progreso)
├── requirements.txt               -> Lista de dependencias
├── .gitignore                     -> Archivos excluidos del repo
└── README.md                      -> Documentación del proyecto

DEPENDENCIAS
------------
Instaladas vía apt y pip en un entorno venv con --system-site-packages:

sudo apt install python3-opencv
pip install flask django mysql-connector-python mediapipe numpy matplotlib pandas

ESTADO FUNCIONAL ACTUAL
------------------------
- El script vision.py:
  - Accede a /dev/video0 usando cv2.CAP_V4L2.
  - Carga el modelo desde archivos .prototxt y .caffemodel.
  - Detecta rostros e imprime coordenadas y confianza en terminal.
  - Libera correctamente la cámara al finalizar.
- El script reset_cam.sh permite recuperar la cámara si quedó bloqueada.

PRÓXIMAS METAS
--------------
1. Agregar servidor Flask:
   - Streaming MJPEG desde navegador.
   - API REST para número de rostros detectados.
2. Implementar pruebas automatizadas.
3. Configurar servicio systemd para arranque automático.
4. Documentar a nivel técnico y usuario.
5. Consolidar el repositorio como respaldo de prácticas profesionales.

LICENCIA
--------
MIT License — libre para uso, modificación y distribución.

AUTORES
-----
Luis Fernando Rodriguez Cruz & Nayeli Ortiz Garcia
Desarrollado en una Raspberry Pi sin entorno gráfico, accediendo vía SSH desde Visual Studio Code.
