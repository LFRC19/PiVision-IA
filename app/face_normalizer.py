import cv2
import numpy as np

class FaceNormalizer:
    def __init__(self, output_size=(128, 128)):
        self.output_size = output_size  # tamaño final (ancho, alto)

    def normalize(self, frame, landmarks):
        """
        Normaliza el rostro basado en los landmarks del rostro completo.
        Usa los ojos para alinear horizontalmente y recorta un ROI centrado.
        """
        if len(landmarks) < 468:
            return None

        # Puntos clave de los ojos
        left_eye = landmarks[33]
        right_eye = landmarks[263]

        # Calcular el ángulo de inclinación
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        angle = np.degrees(np.arctan2(dy, dx))

        # Centro entre los ojos
        eyes_center = ((left_eye[0] + right_eye[0]) // 2,
                       (left_eye[1] + right_eye[1]) // 2)

        # Obtener la matriz de rotación
        M = cv2.getRotationMatrix2D(eyes_center, angle, scale=1.0)

        # Rotar imagen completa
        aligned = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))

        # Calcular bounding box centrado en los ojos
        x, y = eyes_center
        w, h = self.output_size
        x1 = max(x - w // 2, 0)
        y1 = max(y - h // 3, 0)  # desplazar hacia arriba para incluir frente
        x2 = min(x1 + w, frame.shape[1])
        y2 = min(y1 + h, frame.shape[0])

        face_crop = aligned[y1:y2, x1:x2]
        if face_crop.shape[0] <= 0 or face_crop.shape[1] <= 0:
            return None

        # Redimensionar al tamaño estándar
        return cv2.resize(face_crop, self.output_size)
