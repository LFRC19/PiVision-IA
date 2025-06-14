from app.camera_manager import CameraManager
import cv2

# Carga del modelo
net = cv2.dnn.readNetFromCaffe("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000_fp16.caffemodel")

# Inicia la cámara
cam = CameraManager()
cam.start()

try:
    while True:
        frame = cam.read_frame()
        if frame is None:
            continue

        # Preprocesamiento y detección
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
        net.setInput(blob)
        detections = net.forward()

        # Analiza resultados
        h, w = frame.shape[:2]
        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            if conf > 0.5:
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (x1, y1, x2, y2) = box.astype("int")
                print(f"Rostro detectado: Confianza {conf:.2f} | Coordenadas: ({x1},{y1}) - ({x2},{y2})")

except KeyboardInterrupt:
    print("\n[INFO] Interrumpido por el usuario")

finally:
    cam.stop()
    print("[INFO] Cámara liberada correctamente")

