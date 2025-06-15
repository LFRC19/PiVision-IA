import cv2
import mediapipe as mp
import os
import json
from datetime import datetime
from db import Database

class GestureDetector:
    def __init__(self,
                 static_image_mode=False,
                 model_complexity=1,
                 smooth_landmarks=True,
                 enable_segmentation=False,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        """
        Inicializa MediaPipe Holistic para detección de pose y manos.
        """
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process(self, frame):
        """
        Procesa el frame BGR y devuelve un diccionario con:
          - 'pose': lista de tuplas (x,y) de landmarks de pose.
          - 'left_hand': lista de tuplas de landmarks mano izquierda.
          - 'right_hand': lista de tuplas de landmarks mano derecha.
          - 'gestures': lista de gestos detectados (strings).
        Detecta el gesto 'manos_arriba'.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(rgb)

        h, w = frame.shape[:2]
        output = {
            'pose': [],
            'left_hand': [],
            'right_hand': [],
            'gestures': []
        }

        # Extraer pose
        if results.pose_landmarks:
            output['pose'] = [
                (int(lm.x * w), int(lm.y * h))
                for lm in results.pose_landmarks.landmark
            ]

        # Extraer manos
        if results.left_hand_landmarks:
            output['left_hand'] = [
                (int(lm.x * w), int(lm.y * h))
                for lm in results.left_hand_landmarks.landmark
            ]
        if results.right_hand_landmarks:
            output['right_hand'] = [
                (int(lm.x * w), int(lm.y * h))
                for lm in results.right_hand_landmarks.landmark
            ]

        # Detección de "manos arriba"
        pose = output['pose']
        if pose and len(pose) > 16:
            # Índices MediaPipe:
            # 11 hombro izquierdo, 12 hombro derecho,
            # 15 muñeca izquierda, 16 muñeca derecha
            shoulder_y   = (pose[11][1] + pose[12][1]) // 2
            left_wrist_y = pose[15][1]
            right_wrist_y= pose[16][1]
            if left_wrist_y < shoulder_y and right_wrist_y < shoulder_y:
                output['gestures'].append('manos_arriba')

        return output

class GestureHandler:
    def __init__(self, session_dir):
        """
        Maneja la detección de gestos y registra eventos.
        session_dir: carpeta donde guardar imágenes de eventos.
        """
        self.detector    = GestureDetector()
        self.db          = Database()
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)

    def analyze(self, cam_id, frame):
        """
        Ejecuta la detección de gestos en el frame. Por cada gesto:
          - Guarda imagen de evidencia.
          - Registra evento en la BD con event_type='gesture'.
          - Imprime mensaje de consola.
        """
        results = self.detector.process(frame)
        for gesture in results['gestures']:
            timestamp = int(datetime.now().timestamp())
            filename  = os.path.join(
                self.session_dir,
                f"cam{cam_id}_{gesture}_{timestamp}.jpg"
            )
            cv2.imwrite(filename, frame)

            # Registrar en base de datos con tipo genérico para pasar CHECK
            self.db.log_event(
                camera_id    = cam_id,
                event_type   = 'gesture',
                person_id    = None,
                confidence   = 0.0,
                bounding_box = json.dumps({
                    'x': 0, 'y': 0,
                    'w': frame.shape[1],
                    'h': frame.shape[0]
                }),
                image_path   = filename
            )

            print(f"[GESTO] Cam {cam_id}: {gesture} detectado -> {filename}")
