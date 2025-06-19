from flask import Blueprint, jsonify, current_app

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/cameras', methods=['GET'])
def get_cameras():
    """
    Devuelve una lista de cámaras activas con su ID y estado.
    """
    camera_manager = current_app.camera_manager  # instancia de MultiCameraManager
    camera_list = []

    for cam in camera_manager.cams:
        camera_list.append({
            "id": cam.device_id,
            # .running es True si la captura está activa
            "active": cam.running
        })

    return jsonify(camera_list), 200


@api_bp.route('/events', methods=['GET'])
def get_events():
    """
    Devuelve la lista de eventos recientes de todas las cámaras.
    """
    camera_manager = current_app.camera_manager
    all_events = []

    # Recorremos cada cámara para obtener sus eventos
    for cam in camera_manager.cams:
        pipeline = cam.get_pipeline()
        # get_last_events() retorna lista de dicts con clave 'type', 'timestamp', etc.
        events = pipeline.get_last_events()
        for event in events:
            # Añadimos el id de cámara al evento
            event_record = event.copy()
            event_record['camera_id'] = cam.device_id
            all_events.append(event_record)

    return jsonify(all_events), 200
