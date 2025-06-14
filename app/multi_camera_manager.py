import threading
from app.camera_manager import CameraManager

class MultiCameraManager:
    def __init__(self, device_ids, width=640, height=480, fps=30):
        self.cams = [
            CameraManager(device_id=d, width=width, height=height, fps=fps)
            for d in device_ids
        ]

    def start_all(self):
        for cam in self.cams:
            cam.start()

    def read_frames(self):
        """
        Devuelve un dict {device_id: frame}.
        """
        frames = {}
        for cam in self.cams:
            frame = cam.read_frame()
            frames[cam.device_id] = frame
        return frames

    def stop_all(self):
        for cam in self.cams:
            cam.stop()
