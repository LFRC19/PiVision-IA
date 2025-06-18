# app/routes/dashboard.py

import time
import cv2
import psutil
import json
from flask import (
    Blueprint, render_template, Response,
    stream_with_context, current_app, jsonify
)

# 🔐 Importar decorador de autenticación
from app.routes.auth import login_required

# -----------------------------------------------------------------------------  
# Blueprint
# -----------------------------------------------------------------------------  

dashboard_bp = Blueprint('dashboard', __name__)

# -----------------------------------------------------------------------------  
# Vistas HTML
# -----------------------------------------------------------------------------  

@dashboard_bp.route('/')
@login_required
def index():
    """Página principal del dashboard (grid de cámaras)"""
    cam_ids = current_app.camera_manager.device_ids
    return render_template('index.html', camera_ids=cam_ids)

# -----------------------------------------------------------------------------  
# MJPEG Streaming
# -----------------------------------------------------------------------------  

@dashboard_bp.route('/video_feed/<int:camera_id>')
@login_required
def video_feed(camera_id):
    """Endpoint MJPEG: /dashboard/video_feed/<camera_id>"""
    return Response(stream_with_context(gen_mjpeg(camera_id)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_mjpeg(camera_id: int):
    """Generador MJPEG usando el CameraManager del servidor."""
    cam = current_app.camera_manager.get_camera(camera_id)

    if not getattr(cam, 'running', False):
        cam.start()
        time.sleep(0.1)

    while True:
        frame = cam.read_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        ok, jpeg = cv2.imencode('.jpg', frame)
        if not ok:
            time.sleep(0.01)
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

        fps = getattr(cam, 'fps', 30)
        time.sleep(1.0 / fps)

# -----------------------------------------------------------------------------  
# Snapshot único (prueba rápida)
# -----------------------------------------------------------------------------  

@dashboard_bp.route('/snapshot/<int:camera_id>')
@login_required
def snapshot(camera_id):
    """Devuelve una única imagen JPEG capturada en el momento."""
    cam = current_app.camera_manager.get_camera(camera_id)
    if not getattr(cam, 'running', False):
        cam.start()
        time.sleep(0.1)

    frame = cam.read_frame()
    if frame is None:
        return "No hay frame disponible", 503

    ok, jpeg = cv2.imencode('.jpg', frame)
    if not ok:
        return "Error al codificar JPEG", 500

    return Response(jpeg.tobytes(), mimetype='image/jpeg')

# -----------------------------------------------------------------------------  
# Métricas del sistema
# -----------------------------------------------------------------------------  

@dashboard_bp.route('/metrics')
@login_required
def metrics():
    """Devuelve uso de CPU, RAM y disco en JSON."""
    data = {
        'cpu': psutil.cpu_percent(),
        'mem': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage(current_app.config.get('DATA_PATH', '/')).percent,
    }
    return jsonify(data)

# -----------------------------------------------------------------------------  
# Eventos SSE (detecciones IA en tiempo real)
# -----------------------------------------------------------------------------  

@dashboard_bp.route('/events/<int:camera_id>')
@login_required
def stream_events(camera_id):
    """Stream de eventos IA (rostros, movimiento, gestos, conteo) vía SSE."""

    def event_stream():
        with current_app.app_context():
            cam = current_app.camera_manager.get_camera(camera_id)

            if not cam or not getattr(cam, 'running', False):
                return

            while True:
                try:
                    pipeline = cam.get_pipeline()
                    events = pipeline.get_last_events() if pipeline else []
                    print(f"[EVENTOS CAM {camera_id}]: {events}")  # DEBUG
                    yield f"data: {json.dumps(events)}\n\n"
                except Exception as e:
                    print(f"[ERROR SSE CAM {camera_id}]: {e}")
                    yield "data: []\n\n"
                time.sleep(1)

    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')
