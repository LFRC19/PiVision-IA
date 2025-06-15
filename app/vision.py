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
from app.gesture_handler      import GestureHandler

from face_encoder     import FaceEncoder
from face_matcher     import FaceMatcher
from db               import Database
from person_tracker   import CentroidTracker

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

LOG_PATH        = "log/eventos.log"
PRINT_INTERVAL  = 1.0
RECOG_COOLDOWN  = 5.0
ALIGN_DIR       = "rostros"
SESSION_DIR     = os.path.join(ALIGN_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))

# ROI expansion factor
EXPANSION_RATIO = 1.0  # 100%

# Conteo por zonas
track_history = {}
counted_ids_up = {}
counted_ids_down = {}

def log_event_file(cam_id, tipo, mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} | Cam {cam_id} | {tipo} | {mensaje}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PiVision IA con tracking, conteo y reconocimiento facial")
    parser.add_argument("--width",  "-W", type=int, default=640)
    parser.add_argument("--height", "-H", type=int, default=480)
    parser.add_argument("--fps",    "-F", type=int, default=30)
    args = parser.parse_args()

    device_ids = CameraManager.detect_cameras()
    if not device_ids:
        logger.error("No se encontraron cámaras.")
        exit(1)
    logger.info(f"Cámaras detectadas: {device_ids}")

    os.makedirs(SESSION_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    mcam           = MultiCameraManager(device_ids, width=args.width, height=args.height, fps=args.fps)
    motion_proc    = FrameProcessor()
    mesh_processor = FaceMeshProcessor()
    normalizer     = FaceNormalizer()
    encoder        = FaceEncoder()
    matcher        = FaceMatcher(Database(), threshold=0.6)
    tracker        = CentroidTracker(max_disappeared=30, max_distance=50)
    gesture_handler = GestureHandler(SESSION_DIR)

    mcam.start_all()
    last_move   = {cam_id: 0 for cam_id in device_ids}
    last_recog  = {cam_id: 0 for cam_id in device_ids}
    last_count  = {cam_id: 0 for cam_id in device_ids}

    LINE_POSITION = args.height // 2  # línea horizontal

    try:
        while True:
            frames = mcam.read_frames()
            for cam_id, frame in frames.items():
                if frame is None:
                    continue

                now = time.time()
                h, w = frame.shape[:2]

                # 1) Detección de movimiento
                thresh, contours = motion_proc.detect_motion(frame)
                if contours and now - last_move[cam_id] >= PRINT_INTERVAL:
                    logger.info(f"[Movimiento] Cam {cam_id}: {len(contours)} contornos detectados")
                    log_event_file(cam_id, "movimiento", f"{len(contours)} contornos detectados")
                    last_move[cam_id] = now

                # 2) Detección facial con MediaPipe
                rects = []
                mesh_faces = mesh_processor.process(frame)
                for landmarks in mesh_faces:
                    norm_face = normalizer.normalize(frame, landmarks)
                    if norm_face is None:
                        continue

                    xs = [int(p[0]) for p in landmarks]
                    ys = [int(p[1]) for p in landmarks]
                    x, y = min(xs), min(ys)
                    w_box = max(xs) - x
                    h_box = max(ys) - y

                    mx = int(w_box * EXPANSION_RATIO)
                    my = int(h_box * EXPANSION_RATIO)
                    x0 = max(x - mx, 0)
                    y0 = max(y - my, 0)
                    x1 = min(x + w_box + mx, w)
                    y1 = min(y + h_box + my, h)

                    rects.append((x0, y0, x1 - x0, y1 - y0))

                    if now - last_recog[cam_id] >= RECOG_COOLDOWN:
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

                        roi = frame[y0:y1, x0:x1]
                        filename = f"{SESSION_DIR}/cam{cam_id}_{label}_{int(now)}.jpg"
                        cv2.imwrite(filename, roi)

                        log_event_file(cam_id, event_type, f"{label} (conf {confidence:.2f}) => {os.path.basename(filename)}")
                        matcher.db.log_event(
                            camera_id    = cam_id,
                            event_type   = event_type,
                            person_id    = person_id,
                            confidence   = confidence,
                            bounding_box = json.dumps({'x': x0, 'y': y0, 'w': x1 - x0, 'h': y1 - y0}),
                            image_path   = filename
                        )
                        logger.info(f"[Reconocimiento] Cam {cam_id}: {label} (conf {confidence:.2f}) -> {filename}")
                        last_recog[cam_id] = now

                # 3) Detección de gestos
                gesture_handler.analyze(cam_id, frame)

                # 4) Tracking y conteo
                objects = tracker.update(rects)

                if cam_id not in track_history:
                    track_history[cam_id] = {}
                    counted_ids_up[cam_id] = set()
                    counted_ids_down[cam_id] = set()

                cv2.line(frame, (0, LINE_POSITION), (w, LINE_POSITION), (255, 0, 0), 2)

                for object_id, (cx, cy) in objects.items():
                    center_y = cy
                    prev_cy = track_history[cam_id].get(object_id, center_y)
                    track_history[cam_id][object_id] = center_y

                    if prev_cy < LINE_POSITION and center_y >= LINE_POSITION:
                        if object_id not in counted_ids_down[cam_id]:
                            counted_ids_down[cam_id].add(object_id)
                            logger.info(f"[Conteo ↓] Cam {cam_id}: Persona {object_id} cruzó de ARRIBA a ABAJO")
                            log_event_file(cam_id, "conteo_bajada", f"Persona ID {object_id}")
                            filename = f"{SESSION_DIR}/cam{cam_id}_cruce_down_{int(now)}.jpg"
                            cv2.imwrite(filename, frame)
                            matcher.db.log_event(
                                camera_id    = cam_id,
                                event_type   = "zone_cross_down",
                                person_id    = None,
                                confidence   = 0.0,
                                bounding_box = json.dumps({'x': 0, 'y': LINE_POSITION, 'w': w, 'h': 2}),
                                image_path   = filename
                            )

                    elif prev_cy > LINE_POSITION and center_y <= LINE_POSITION:
                        if object_id not in counted_ids_up[cam_id]:
                            counted_ids_up[cam_id].add(object_id)
                            logger.info(f"[Conteo ↑] Cam {cam_id}: Persona {object_id} cruzó de ABAJO a ARRIBA")
                            log_event_file(cam_id, "conteo_subida", f"Persona ID {object_id}")
                            filename = f"{SESSION_DIR}/cam{cam_id}_cruce_up_{int(now)}.jpg"
                            cv2.imwrite(filename, frame)
                            matcher.db.log_event(
                                camera_id    = cam_id,
                                event_type   = "zone_cross_up",
                                person_id    = None,
                                confidence   = 0.0,
                                bounding_box = json.dumps({'x': 0, 'y': LINE_POSITION, 'w': w, 'h': 2}),
                                image_path   = filename
                            )

                if now - last_count[cam_id] >= PRINT_INTERVAL:
                    logger.info(f"[Detección] Cam {cam_id}: {len(objects)} persona{'s' if len(objects) != 1 else ''} presentes")
                    last_count[cam_id] = now

            time.sleep(1.0 / args.fps)

    except KeyboardInterrupt:
        logger.info("Interrumpido por el usuario")

    finally:
        mcam.stop_all()
        logger.info("Cámaras liberadas correctamente")
