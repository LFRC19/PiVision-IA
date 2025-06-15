# app/routes/dashboard.py

import time
import cv2
import psutil
from flask import (
    Blueprint, render_template, Response,
    stream_with_context, current_app, jsonify
)

# -----------------------------------------------------------------------------
# Blueprint
# -----------------------------------------------------------------------------

dashboard_bp = Blueprint('dashboard', __name__)

# -----------------------------------------------------------------------------
# Vistas HTML
# -----------------------------------------------------------------------------

@dashboard_bp.route('/')
def index():
    """Página principal del dashboard (grid de cámaras)"""
    cam_ids = current_app.camera_manager.device_ids
    return render_template('dashboard.html', camera_ids=cam_ids)

# -----------------------------------------------------------------------------
# MJPEG Streaming
# -----------------------------------------------------------------------------

def gen_mjpeg(camera_id: int):
    """Generador MJPEG usando el CameraManager del servidor."""
    cam = current_app.camera_manager.get_camera(camera_id)

    # Garantizamos que el hilo de captura esté activo
    if not getattr(cam, 'running', False):
        cam.start()
        time.sleep(0.1)  # da tiempo a que llegue el primer frame

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

        # Regulamos FPS (~30 fps)
        fps = getattr(cam, 'fps', 30)
        time.sleep(1.0 / fps)


@dashboard_bp.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    """Endpoint MJPEG: /dashboard/video_feed/<camera_id>"""
    return Response(stream_with_context(gen_mjpeg(camera_id)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# -----------------------------------------------------------------------------
# Snapshot único (prueba rápida)
# -----------------------------------------------------------------------------

@dashboard_bp.route('/snapshot/<int:camera_id>')
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
def metrics():
    """Devuelve uso de CPU, RAM y disco en JSON."""
    data = {
        'cpu': psutil.cpu_percent(),
        'mem': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage(current_app.config.get('DATA_PATH', '/')).percent,
    }
    return jsonify(data)

