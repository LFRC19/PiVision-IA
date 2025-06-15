#!/usr/bin/env python3
import argparse
import os
import time
import json
from datetime import datetime
import logging
import cv2

from app.multi_camera_manager import MultiCameraManager
from app.camera_manager       import CameraManager
from app.frame_processor      import FrameProcessor
from app.face_mesh_processor  import FaceMeshProcessor
from app.face_normalizer      import FaceNormalizer

from face_encoder import FaceEncoder
from face_matcher import FaceMatcher
from db           import Database

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

LOG_PATH       = "log/eventos.log"
PRINT_INTERVAL = 1.0
ALIGN_DIR      = "rostros"
RECOG_COOLDOWN = 5.0  # segundos mínimo entre registros de reconocimiento

# Directorio de sesión para guardado de rostros
SESSION_DIR = os.path.join(ALIGN_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))


def log_event_file(cam_id, tipo, mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} | Cam {cam_id} | {tipo} | {mensaje}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PiVision IA headless con reconocimiento facial y BD")
    parser.add_argument("--width",  "-W", type=int, default=640)
    parser.add_argument("--height","-H", type=int, default=480)
    parser.add_argument("--fps",   "-F", type=int, default=30)
    args = parser.parse_args()

    # Inicializar cámaras
    device_ids = CameraManager.detect_cameras()
    if not device_ids:
        logger.error("No se encontraron cámaras.")
        exit(1)
    logger.info(f"Cámaras detectadas: {device_ids}")

    # Crear directorio de sesión
    os.makedirs(SESSION_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    # Inicialización de managers y procesadores
    mcam           = MultiCameraManager(device_ids, width=args.width, height=args.height, fps=args.fps)
    motion_proc    = FrameProcessor()
    mesh_processor = FaceMeshProcessor()
    normalizer     = FaceNormalizer()
    mcam.start_all()

    # Estado de cooldowns
    last_move     = {cam_id: 0 for cam_id in device_ids}
    last_recog    = {cam_id: 0 for cam_id in device_ids}

    # Inicializar sistema de reconocimiento
    db      = Database()
    encoder = FaceEncoder()
    matcher = FaceMatcher(db, threshold=0.6)

    try:
        while True:
            frames = mcam.read_frames()
            for cam_id, frame in frames.items():
                if frame is None:
                    continue

                now = time.time()

                # Detección de movimiento
                thresh, contours = motion_proc.detect_motion(frame)
                if contours and now - last_move[cam_id] >= PRINT_INTERVAL:
                    msg = f"{len(contours)} contornos detectados"
                    logger.info(f"[Movimiento] Cam {cam_id}: {msg}")
                    log_event_file(cam_id, "movimiento", msg)
                    last_move[cam_id] = now

                # Face Mesh + normalización
                mesh_faces = mesh_processor.process(frame)
                for landmarks in mesh_faces:
                    norm_face = normalizer.normalize(frame, landmarks)
                    if norm_face is None:
                        continue

                    # Encoding y matching
                    embedding = encoder.encode(norm_face)
                    result    = matcher.match(embedding)
                    if result:
                        event_type = "face_detected"
                        person_id  = result["id"]
                        label      = result["name"]
                        confidence = result["distance"]
                    else:
                        event_type = "unknown_person"
                        person_id  = None
                        label      = "Desconocido"
                        confidence = 0.0

                    # Solo registrar reconocimiento si supera cooldown
                    if now - last_recog[cam_id] >= RECOG_COOLDOWN:
                        # Bounding box a partir de landmarks
                        xs = [int(p[0]) for p in landmarks]
                        ys = [int(p[1]) for p in landmarks]
                        x, y = min(xs), min(ys)
                        w, h = max(xs) - x, max(ys) - y

                        # Guardar imagen normalizada
                        filename = f"{SESSION_DIR}/cam{cam_id}_{label}_{int(now)}.jpg"
                        cv2.imwrite(filename, norm_face)

                        # Logging
                        log_event_file(cam_id, event_type, f"{label} => {os.path.basename(filename)}")
                        db.log_event(
                            camera_id    = cam_id,
                            event_type   = event_type,
                            person_id    = person_id,
                            confidence   = confidence,
                            bounding_box = json.dumps({'x': x, 'y': y, 'w': w, 'h': h}),
                            image_path   = filename
                        )

                        logger.info(f"[Reconocimiento] Cam {cam_id}: {label} (conf {confidence:.2f}) -> {filename}")
                        last_recog[cam_id] = now

            # Control de FPS en modo headless
            time.sleep(1.0 / args.fps)

    except KeyboardInterrupt:
        logger.info("Interrumpido por el usuario")

    finally:
        mcam.stop_all()
        logger.info("Cámaras liberadas correctamente")
