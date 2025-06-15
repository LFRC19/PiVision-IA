# app/camera_manager.py

import cv2, threading, time
from app.ai_engine import AIPipeline

class CameraManager:
    def __init__(self, device_id, width=640, height=480, fps=30):
        self.device_id = device_id
        self.width, self.height, self.fps = width, height, fps
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

        # Instancia del motor IA para esta cámara
        self.pipeline = AIPipeline(device_id, width, height)

    def start(self):
        if self.running:
            return

        self.cap = cv2.VideoCapture(self.device_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {self.device_id}")

        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.resize(frame, (self.width, self.height))

            # Procesamiento IA
            processed_frame, _ = self.pipeline.process(frame)

            with self.lock:
                self.frame = processed_frame

    def read_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def get_pipeline(self):
        return self.pipeline

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
