# app/multi_camera_manager.py

import threading
import logging
from app.camera_manager import CameraManager

class MultiCameraManager:
    def __init__(self, device_ids, width=640, height=480, fps=30):
        """Inicializa múltiples cámaras con los parámetros indicados."""
        self.cams = [
            CameraManager(device_id=d, width=width, height=height, fps=fps)
            for d in device_ids
        ]

    def start_all(self):
        """Inicia todas las cámaras que se pudieron abrir correctamente."""
        valid = []
        for cam in self.cams:
            try:
                cam.start()
                valid.append(cam)
            except Exception as e:
                logging.warning(f"No se pudo iniciar cámara {cam.device_id}: {e}")
        self.cams = valid

    def stop_all(self):
        """Detiene todas las cámaras activas."""
        for cam in self.cams:
            cam.stop()

    def read_frames(self):
        """Devuelve un diccionario {device_id: frame} para todas las cámaras."""
        frames = {}
        for cam in self.cams:
            frame = cam.read_frame()
            frames[cam.device_id] = frame
        return frames

    def get_camera(self, device_id):
        """Devuelve la cámara con el ID solicitado o None si no existe."""
        for cam in self.cams:
            if cam.device_id == device_id:
                return cam
        return None  # ← importante para evitar errores en /events

    @property
    def device_ids(self):
        """Lista de IDs de cámaras actualmente activas."""
        return [cam.device_id for cam in self.cams]
