# app/camera_manager.py

import cv2, threading, time
from app.ai_engine import AIPipeline

# ---------------------------------------------------------------------
# Cámara individual
# ---------------------------------------------------------------------
class Camera:
    def __init__(self, device_id, width=640, height=480, fps=30):
        self.device_id = device_id
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

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

# ---------------------------------------------------------------------
# Manager para múltiples cámaras
# ---------------------------------------------------------------------
class CameraManager:
    def __init__(self, device_ids, width=640, height=480, fps=30):
        self.device_ids = device_ids
        self.cameras = {}
        self.width = width
        self.height = height
        self.fps = fps

        for cam_id in device_ids:
            self.cameras[cam_id] = Camera(cam_id, width, height, fps)

    def get_camera(self, cam_id):
        return self.cameras.get(cam_id)

    def get_camera_list(self):
        return list(self.cameras.keys())

    def generate(self, cam_id):
        cam = self.get_camera(cam_id)
        if not cam:
            return

        if not getattr(cam, 'running', False):
            cam.start()
            time.sleep(0.1)

        while True:
            frame = cam.read_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            ok, jpeg = cv2.imencode('.jpg', frame)
            if not ok:
                time.sleep(0.01)
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

            time.sleep(1.0 / self.fps)

    @classmethod
    def detect_cameras(cls, max_test=5):
        ids = []
        for i in range(max_test):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ids.append(i)
                cap.release()
        return ids
