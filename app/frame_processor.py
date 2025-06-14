import cv2
import numpy as np

class FrameProcessor:
    def __init__(self):
        self.previous_frame = None

    def preprocess(self, frame, blur_type="gaussian", kernel_size=(5, 5)):
        """
        Convierte a escala de grises y aplica desenfoque para reducir ruido.
        blur_type: 'gaussian' o 'median'
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if blur_type == "gaussian":
            gray = cv2.GaussianBlur(gray, kernel_size, 0)
        elif blur_type == "median":
            gray = cv2.medianBlur(gray, kernel_size[0])  # sólo necesita un valor
        return gray

    def detect_motion(self, frame):
        """
        Compara el frame actual con el anterior y detecta regiones con movimiento.
        Devuelve el umbral binarizado y una lista de contornos.
        """
        gray = self.preprocess(frame)

        if self.previous_frame is None:
            self.previous_frame = gray
            return None, None

        diff = cv2.absdiff(self.previous_frame, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        self.previous_frame = gray

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return thresh, contours
