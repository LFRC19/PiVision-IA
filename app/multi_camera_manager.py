# app/multi_camera_manager.py

import logging
from app.camera_manager import CameraManager

class MultiCameraManager:
    def __init__(self, device_ids, width=640, height=480, fps=30):
        """Inicializa un solo CameraManager que maneja todas las cámaras."""
        self.manager = CameraManager(device_ids=device_ids, width=width, height=height, fps=fps)
        self.start_all()

    def start_all(self):
        """Inicia todas las cámaras válidas."""
        for cam_id in self.manager.device_ids:
            try:
                cam = self.manager.get_camera(cam_id)
                cam.start()
            except Exception as e:
                logging.warning(f"No se pudo iniciar cámara {cam_id}: {e}")

    def stop_all(self):
        """Detiene todas las cámaras activas."""
        for cam_id in self.manager.device_ids:
            cam = self.manager.get_camera(cam_id)
            if cam:
                cam.stop()

    def read_frames(self):
        """Devuelve un diccionario {device_id: frame} de todas las cámaras."""
        frames = {}
        for cam_id in self.manager.device_ids:
            cam = self.manager.get_camera(cam_id)
            frame = cam.read_frame() if cam else None
            frames[cam_id] = frame
        return frames

    def get_camera(self, device_id):
        """Acceso directo al objeto Camera desde CameraManager."""
        return self.manager.get_camera(device_id)

    @property
    def device_ids(self):
        """Lista de IDs de cámaras actualmente activas."""
        return self.manager.get_camera_list()
