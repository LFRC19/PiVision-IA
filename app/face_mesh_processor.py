import cv2
import mediapipe as mp

class FaceMeshProcessor:
    def __init__(self, static_mode=False, max_faces=1, min_detection_conf=0.5, min_tracking_conf=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_mode,
            max_num_faces=max_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_conf,
            min_tracking_confidence=min_tracking_conf
        )

    def process(self, frame):
        """
        Devuelve una lista de listas con los puntos (x, y) por cada rostro detectado.
        Las coordenadas están en pixeles respecto al tamaño original del frame.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mesh.process(rgb)

        if not results.multi_face_landmarks:
            return []

        h, w = frame.shape[:2]
        all_faces = []

        for face_landmarks in results.multi_face_landmarks:
            points = []
            for lm in face_landmarks.landmark:
                x, y = int(lm.x * w), int(lm.y * h)
                points.append((x, y))
            all_faces.append(points)

        return all_faces
