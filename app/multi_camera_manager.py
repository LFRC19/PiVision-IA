# app/multi_camera_manager.py

import threading
import logging
from app.camera_manager import CameraManager

class MultiCameraManager:
    def __init__(self, device_ids, width=640, height=480, fps=30):
        self.cams = [
            CameraManager(device_id=d, width=width, height=height, fps=fps)
            for d in device_ids
        ]

    def start_all(self):
        valid = []
        for cam in self.cams:
            try:
                cam.start()
                valid.append(cam)
            except Exception as e:
                logging.warning(f"No se pudo iniciar cámara {cam.device_id}: {e}")
        self.cams = valid

    def read_frames(self):
        frames = {}
        for cam in self.cams:
            frame = cam.read_frame()
            frames[cam.device_id] = frame
        return frames

    def stop_all(self):
        for cam in self.cams:
            cam.stop()

    @property
    def device_ids(self):
        return [cam.device_id for cam in self.cams]

    def get_camera(self, device_id):
        for cam in self.cams:
            if cam.device_id == device_id:
                return cam
        raise ValueError(f"No existe cámara con device_id={device_id}")
