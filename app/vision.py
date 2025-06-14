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

LOG_PATH = "log/eventos.log"
PRINT_INTERVAL = 1.0  # segundos mínimo entre prints por cámara

def log_event(cam_id, tipo, mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"{timestamp} | Cam {cam_id} | {tipo} | {mensaje}\n")

parser = argparse.ArgumentParser(description="PiVision IA: Caffe + MediaPipe + Movimiento")
parser.add_argument("--width", "-W", type=int, default=640)
parser.add_argument("--height", "-H", type=int, default=480)
parser.add_argument("--fps", "-F", type=int, default=30)
args = parser.parse_args()

# Detectar cámaras
device_ids = CameraManager.detect_cameras()
if not device_ids:
    print("[ERROR] No se encontraron cámaras.")
    exit(1)
print(f"[INFO] Cámaras detectadas: {device_ids}")

# Inicializar componentes
mcam = MultiCameraManager(device_ids, width=args.width, height=args.height, fps=args.fps)
processor = FrameProcessor()
mp_detector = FaceDetector()
mesh_processor = FaceMeshProcessor()

mcam.start_all()
last_print = {cam_id: 0 for cam_id in device_ids}

# Modelo DNN de Caffe
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

            # Detección facial (Caffe)
            blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
            net.setInput(blob)
            detections = net.forward()

            h, w = frame.shape[:2]
            for i in range(detections.shape[2]):
                conf = float(detections[0, 0, i, 2])
                if conf > 0.5 and now - last_print[cam_id] >= PRINT_INTERVAL:
                    box = (detections[0, 0, i, 3:7] * [w, h, w, h]).astype("int")
                    x1, y1, x2, y2 = box
                    msg = f"conf={conf:.2f}, coords=({x1},{y1})-({x2},{y2}) [Caffe]"
                    print(f"[Caffe-Face] Cam {cam_id}: {msg}")
                    log_event(cam_id, "caffe_rostro", msg)
                    last_print[cam_id] = now

            # Detección facial (MediaPipe)
            mp_detections = mp_detector.detect(frame)
            if mp_detections:
                for d in mp_detections:
                    score = d['score']
                    x1, y1, x2, y2 = d['bbox']
                    if now - last_print[cam_id] >= PRINT_INTERVAL:
                        msg = f"conf={score:.2f}, coords=({x1},{y1})-({x2},{y2}) [MediaPipe]"
                        print(f"[MP-Face] Cam {cam_id}: {msg}")
                        log_event(cam_id, "mp_rostro", msg)
                        last_print[cam_id] = now

            # Landmarks con FaceMesh
            mesh_faces = mesh_processor.process(frame)
            for face_idx, landmarks in enumerate(mesh_faces):
                nose = landmarks[1]  # punto 1 = punta de nariz
                if now - last_print[cam_id] >= PRINT_INTERVAL:
                    msg = f"Face {face_idx}: Nose at {nose} [Mesh]"
                    print(f"[Mesh] Cam {cam_id}: {msg}")
                    log_event(cam_id, "landmarks", msg)
                    last_print[cam_id] = now

except KeyboardInterrupt:
    print("\n[INFO] Interrumpido por el usuario")

finally:
    mcam.stop_all()
    print("[INFO] Cámaras liberadas correctamente")
