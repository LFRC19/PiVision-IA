import mediapipe as mp
import cv2

class FaceDetector:
    def __init__(self, min_detection_confidence=0.5):
        self.mp_face = mp.solutions.face_detection
        self.detector = self.mp_face.FaceDetection(min_detection_confidence)

    def detect(self, frame):
        """
        Recibe un frame BGR, devuelve lista de detecciones con:
        {
            'bbox': (x1, y1, x2, y2),
            'score': float
        }
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb)
        detections = []

        if results.detections:
            h, w = frame.shape[:2]
            for det in results.detections:
                box = det.location_data.relative_bounding_box
                x1 = int(box.xmin * w)
                y1 = int(box.ymin * h)
                x2 = x1 + int(box.width * w)
                y2 = y1 + int(box.height * h)
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'score': det.score[0]
                })

        return detections
