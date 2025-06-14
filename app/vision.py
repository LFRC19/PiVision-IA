#!/usr/bin/env python3
import argparse
import cv2
import os
import time
from datetime import datetime

from app.multi_camera_manager import MultiCameraManager
from app.camera_manager import CameraManager
from app.frame_processor import FrameProcessor
from app.face_detector import FaceDetector
from app.face_mesh_processor import FaceMeshProcessor
from app.face_normalizer import FaceNormalizer
from app.face_signature import extract_signature, is_similar

LOG_PATH = "log/eventos.log"
PRINT_INTERVAL = 1.0
OUTPUT_DIR = "rostros"
SIGNATURE_THRESHOLD = 0.05  # sensibilidad de comparación

def log_event(cam_id, tipo, mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} | Cam {cam_id} | {tipo} | {mensaje}\n")

parser = argparse.ArgumentParser(description="PiVision IA con deduplicación de rostros")
parser.add_argument("--width", "-W", type=int, default=640)
parser.add_argument("--height", "-H", type=int, default=480)
parser.add_argument("--fps", "-F", type=int, default=30)
args = parser.parse_args()

device_ids = CameraManager.detect_cameras()
if not device_ids:
    print("[ERROR] No se encontraron cámaras.")
    exit(1)
print(f"[INFO] Cámaras detectadas: {device_ids}")

mcam = MultiCameraManager(device_ids, width=args.width, height=args.height, fps=args.fps)
processor = FrameProcessor()
mp_detector = FaceDetector()
mesh_processor = FaceMeshProcessor()
normalizer = FaceNormalizer()
mcam.start_all()
last_print = {cam_id: 0 for cam_id in device_ids}
recent_signatures = {cam_id: [] for cam_id in device_ids}

os.makedirs(OUTPUT_DIR, exist_ok=True)

net = cv2.dnn.readNetFromCaffe(
    "models/deploy.prototxt",
    "models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
)

try:
    while True:
        frames = mcam.read_frames()
        for cam_id, frame in frames.items():
            if frame is None:
                continue

            now = time.time()
            gray = processor.preprocess(frame)

            # Movimiento
            thresh, contours = processor.detect_motion(frame)
            if contours and now - last_print[cam_id] >= PRINT_INTERVAL:
                msg = f"{len(contours)} contornos detectados"
                print(f"[Movimiento] Cam {cam_id}: {msg}")
                log_event(cam_id, "movimiento", msg)
                last_print[cam_id] = now

            # Face Mesh + Normalización y Firma
            mesh_faces = mesh_processor.process(frame)
            for face_idx, landmarks in enumerate(mesh_faces):
                sig = extract_signature(landmarks, frame.shape)

                # Comparar con firmas recientes
                if any(is_similar(sig, s, SIGNATURE_THRESHOLD) for s in recent_signatures[cam_id]):
                    continue  # rostro ya visto recientemente

                # Agregar nueva firma
                recent_signatures[cam_id].append(sig)
                if len(recent_signatures[cam_id]) > 10:
                    recent_signatures[cam_id].pop(0)  # mantener tamaño fijo

                # Normalizar rostro y guardar
                norm_face = normalizer.normalize(frame, landmarks)
                if norm_face is not None:
                    filename = f"{OUTPUT_DIR}/cam{cam_id}_face{face_idx}_{int(now)}.jpg"
                    cv2.imwrite(filename, norm_face)
                    msg = f"[DEDUP] Face {face_idx} nueva: Nose {landmarks[1]} => {os.path.basename(filename)}"
                    print(f"[Mesh] Cam {cam_id}: {msg}")
                    log_event(cam_id, "rostro_nuevo", msg)

except KeyboardInterrupt:
    print("\n[INFO] Interrumpido por el usuario")

finally:
    mcam.stop_all()
    print("[INFO] Cámaras liberadas correctamente")
