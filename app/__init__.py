# app/__init__.py

import os
from pathlib import Path
from flask import Flask, render_template
from app.camera_manager import CameraManager
from app.multi_camera_manager import MultiCameraManager

def create_app():
    # 1) Crear app
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    # 2) Cargar configuración (incluye CAMERA_IDS = [0,1] u otra lista)
    base_dir    = Path(__file__).resolve().parent.parent
    config_path = base_dir / 'config' / 'settings.py'
    if config_path.is_file():
        app.config.from_pyfile(str(config_path))
    else:
        app.logger.warning(f"No se encontró {config_path}, usando valores por defecto.")
        # por defecto no forzamos ningún ID
        app.config.setdefault('CAMERA_IDS', [])

    # 3) Detectar cámaras reales y cruzar con lo configurado
    configured = app.config.get('CAMERA_IDS', [])
    detected   = CameraManager.detect_cameras()
    # Solo nos quedamos con los IDs válidos
    device_ids = [i for i in configured if i in detected]
    if not device_ids:
        app.logger.error(f"Ningún ID configurado {configured} está disponible. Cámaras detectadas: {detected}")
    else:
        app.logger.info(f"Inicializando sólo cámaras válidas: {device_ids}")

    # 4) Instanciar y arrancar cámaras (solo en el proceso que sirve peticiones)
    manager = MultiCameraManager(device_ids=device_ids)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        manager.start_all()
    app.camera_manager = manager

    # 5) Ruta raíz: renderiza index.html con la lista final de cámaras
    @app.route('/')
    def home():
        return render_template('index.html', camera_ids=device_ids)

    # 6) Registrar Blueprint del dashboard
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # 7) Asegurarnos de parar las cámaras al shutdown
    @app.teardown_appcontext
    def shutdown_manager(exc=None):
        app.camera_manager.stop_all()

    return app
