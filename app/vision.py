#!/usr/bin/env python3
import argparse
import cv2
from app.multi_camera_manager import MultiCameraManager
from app.camera_manager import CameraManager

# --- Parseo de argumentos ---
parser = argparse.ArgumentParser(
    description="PiVision IA: detección de rostros headless con múltiples cámaras"
)
parser.add_argument("--width", "-W", type=int, default=640, help="Ancho (px)")
parser.add_argument("--height", "-H", type=int, default=480, help="Altura (px)")
parser.add_argument("--fps", "-F", type=int, default=30, help="FPS")
args = parser.parse_args()

# --- Detectar cámaras disponibles ---
device_ids = CameraManager.detect_cameras()
if not device_ids:
    print("[ERROR] No se encontraron cámaras disponibles.")
    exit(1)
print(f"[INFO] Cámaras detectadas: {device_ids}")

# --- Iniciar todos los streams ---
mcam = MultiCameraManager(
    device_ids=device_ids,
    width=args.width,
    height=args.height,
    fps=args.fps
)
mcam.start_all()
print(f"[INFO] Iniciadas cámaras @ {args.width}x{args.height} @ {args.fps}fps")

# --- Carga del modelo DNN ---
net = cv2.dnn.readNetFromCaffe(
    "models/deploy.prototxt",
    "models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
)

try:
    while True:
        frames = mcam.read_frames()
        for dev_id, frame in frames.items():
            if frame is None:
                continue

            # Preprocesamiento y detección
            blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
            net.setInput(blob)
            detections = net.forward()

            h, w = frame.shape[:2]
            for i in range(detections.shape[2]):
                conf = float(detections[0, 0, i, 2])
                if conf > 0.5:
                    box = (detections[0, 0, i, 3:7] * [w, h, w, h]).astype("int")
                    x1, y1, x2, y2 = box
                    print(
                        f"[Cam {dev_id}] Rostro detectado: conf={conf:.2f} "
                        f"coords=({x1},{y1})-({x2},{y2})"
                    )

except KeyboardInterrupt:
    print("\n[INFO] Interrumpido por el usuario")

finally:
    mcam.stop_all()
    print("[INFO] Todas las cámaras liberadas correctamente")
