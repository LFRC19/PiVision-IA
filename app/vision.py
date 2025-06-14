#!/usr/bin/env python3
import argparse
import cv2
from app.camera_manager import CameraManager

# --- Parseo de argumentos ---
parser = argparse.ArgumentParser(
    description="PiVision IA: detección de rostros headless con parámetros de cámara"
)
parser.add_argument(
    "--width", "-W", type=int, default=640,
    help="Ancho de la captura (px)"
)
parser.add_argument(
    "--height", "-H", type=int, default=480,
    help="Altura de la captura (px)"
)
parser.add_argument(
    "--fps", "-F", type=int, default=30,
    help="Frames por segundo de la captura"
)
args = parser.parse_args()

# --- Detección automática de cámaras ---
candidates = CameraManager.detect_cameras()
if not candidates:
    print("[ERROR] No se encontraron cámaras disponibles.")
    exit(1)

# --- Inicialización de la cámara con parámetros ---
cam = CameraManager(
    device_id=candidates[0],
    width=args.width,
    height=args.height,
    fps=args.fps
)
cam.start()
print(f"[INFO] Usando /dev/video{candidates[0]} @ {args.width}x{args.height} @ {args.fps}fps")

# --- Carga del modelo DNN ---
net = cv2.dnn.readNetFromCaffe(
    "models/deploy.prototxt",
    "models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
)

try:
    while True:
        frame = cam.read_frame()
        if frame is None:
            continue

        blob = cv2.dnn.blobFromImage(
            frame, 1.0, (300, 300), (104, 177, 123)
        )
        net.setInput(blob)
        detections = net.forward()

        h, w = frame.shape[:2]
        for i in range(detections.shape[2]):
            conf = float(detections[0, 0, i, 2])
            if conf > 0.5:
                box = (detections[0, 0, i, 3:7] * [w, h, w, h]).astype("int")
                x1, y1, x2, y2 = box
                print(
                    f"Rostro detectado: conf={conf:.2f} "
                    f"coords=({x1},{y1})-({x2},{y2})"
                )

except KeyboardInterrupt:
    print("\n[INFO] Interrumpido por el usuario")

finally:
    cam.stop()
    print("[INFO] Cámara liberada correctamente")
