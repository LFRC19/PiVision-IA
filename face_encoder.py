# face_encoder.py

import numpy as np
import cv2
import os
from tflite_runtime.interpreter import Interpreter

# Ajustado el nombre del archivo de modelo para coincidir con el existente en models/
MODEL_FILENAME = 'mobilefacenet.tflite'
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', MODEL_FILENAME)
IMG_SIZE = 112  # Tamaño esperado por MobileFaceNet

class FaceEncoder:
    def __init__(self, model_path: str = MODEL_PATH):
        # Inicializa el intérprete de TFLite usando tflite-runtime
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def preprocess(self, face_img: np.ndarray) -> np.ndarray:
        """
        Redimensiona a (IMG_SIZE, IMG_SIZE) y normaliza la imagen al rango [-1, 1]
        """
        resized = cv2.resize(face_img, (IMG_SIZE, IMG_SIZE))
        normalized = resized.astype(np.float32) / 127.5 - 1.0
        return np.expand_dims(normalized, axis=0)

    def encode(self, face_img: np.ndarray) -> np.ndarray:
        """
        Genera el embedding facial normalizado de la imagen de entrada.
        """
        input_tensor = self.preprocess(face_img)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        embedding = output_data[0]
        # Normaliza el vector para que tenga longitud 1
        norm = np.linalg.norm(embedding)
        return embedding / norm if norm > 0 else embedding
