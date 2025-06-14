import cv2
import threading
import time
import os

class CameraManager:
    def __init__(self, device_id=0, width=640, height=480, fps=30):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.running = False
        self.frame = None
        self.buffer = []
        self.buffer_size = 100
        self.lock = threading.Lock()

    def start(self):
        self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara {self.device_id}")
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            with self.lock:
                self.frame = frame
                self.buffer.append(frame)
                if len(self.buffer) > self.buffer_size:
                    self.buffer.pop(0)
            time.sleep(1 / self.fps)

    def read_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()

    @staticmethod
    def detect_cameras(max_devices=5):
        """Detecta dispositivos /dev/videoX disponibles y operativos"""
        available = []
        for i in range(max_devices):
            path = f"/dev/video{i}"
            if os.path.exists(path):
                cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
                if cap.isOpened():
                    available.append(i)
                    cap.release()
        return available
