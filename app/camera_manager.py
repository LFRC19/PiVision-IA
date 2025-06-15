# app/camera_manager.py (versión simplificada)

import cv2, threading, time

class CameraManager:
    def __init__(self, device_id, width=640, height=480, fps=30):
        self.device_id = device_id
        self.width, self.height, self.fps = width, height, fps
        self.cap = None          # todavía NO abrimos la cámara
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        # Si ya está corriendo no hacemos nada
        if self.running:
            return

        # Abrimos la cámara aquí
        self.cap = cv2.VideoCapture(self.device_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {self.device_id}")

        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                # pequeño respiro antes de volver a intentar
                time.sleep(0.01)
                continue
            frame = cv2.resize(frame, (self.width, self.height))
            with self.lock:
                self.frame = frame

    def read_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    @classmethod
    def detect_cameras(cls, max_test=5):
        ids = []
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ids.append(i)
                cap.release()
        return ids
