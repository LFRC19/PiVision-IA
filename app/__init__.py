import os
from pathlib import Path
from flask import Flask, render_template, redirect, url_for, session
from app.multi_camera_manager import MultiCameraManager
from app.camera_manager import CameraManager  # usado para detectar

def create_app():
    # 1) Crear app Flask
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    # 🔐 Clave secreta para sesiones
    app.secret_key = "clave_super_secreta_123"  # cambia por una clave segura y privada

    # 2) Configuración
    base_dir    = Path(__file__).resolve().parent.parent
    config_path = base_dir / 'config' / 'settings.py'
    if config_path.is_file():
        app.config.from_pyfile(str(config_path))
    else:
        app.logger.warning(f"No se encontró {config_path}, usando valores por defecto.")
        app.config.setdefault('CAMERA_IDS', [])

    # 3) Detectar cámaras reales
    configured = app.config.get('CAMERA_IDS', [])
    detected   = CameraManager.detect_cameras()
    device_ids = [i for i in configured if i in detected]
    if not device_ids:
        app.logger.error(f"Ningún ID configurado {configured} está disponible. Cámaras detectadas: {detected}")
    else:
        app.logger.info(f"Inicializando sólo cámaras válidas: {device_ids}")

    # 4) Instanciar MultiCameraManager
    manager = MultiCameraManager(device_ids=device_ids)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        manager.start_all()

    # ← Esta línea es CRUCIAL para que Blueprint acceda
    app.camera_manager = manager

    # 5) Página raíz → Redirigir a login si no hay sesión
    @app.route('/')
    def home():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return render_template('index.html', camera_ids=device_ids)

    # 6) Registrar Blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.auth import auth_bp
    from app.routes.notifications import notifications_bp  # nuevo blueprint

    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(auth_bp)
    app.register_blueprint(notifications_bp)

    # 7) Liberar recursos al cerrar
    @app.teardown_appcontext
    def shutdown_manager(exc=None):
        app.camera_manager.stop_all()

    return app
