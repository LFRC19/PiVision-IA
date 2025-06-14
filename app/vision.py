#!/usr/bin/env python3
import cv2
import time

# Escoge la cámara (0 por defecto) y backend v4l2
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    print("Error: no se puede abrir la cámara.")
    exit(1)

# Carga modelo
model_cfg  = "../models/deploy.prototxt"
model_weights = "../models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
net = cv2.dnn.readNetFromCaffe(model_cfg, model_weights)

# Parámetros
in_w, in_h = 300, 300
mean_vals = (104, 117, 123)
conf_th = 0.7

print("Iniciando detección (headless). Ctrl+C para parar.")
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fin de video o error de captura.")
            break

        # Prepara blob y obtén detecciones
        blob = cv2.dnn.blobFromImage(frame, 1.0, (in_w, in_h), mean_vals, swapRB=False, crop=False)
        net.setInput(blob)
        detections = net.forward()

        # Recorre detecciones y emite por consola
        h, w = frame.shape[:2]
        for i in range(detections.shape[2]):
            conf = float(detections[0, 0, i, 2])
            if conf > conf_th:
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * h)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * h)
                print(f"[{time.strftime('%H:%M:%S')}] Rostro: confianza={conf:.2f}, bbox=({x1},{y1})-({x2},{y2})")

        # Pausa corta para no saturar la CPU
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nDetención por usuario.")

finally:
    cap.release()
    print("Recursos liberados. Saliendo.")
