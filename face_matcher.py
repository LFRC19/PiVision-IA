# face_matcher.py

import numpy as np
import json
from db import Database

class FaceMatcher:
    def __init__(self, db: Database, threshold: float = 0.6):
        self.db = db
        self.threshold = threshold
        self.known_faces = self._load_known_faces()

    def _load_known_faces(self):
        known = []
        for row in self.db.get_known_faces():
            try:
                vector = np.array(json.loads(row['face_encoding']))
                known.append({
                    'id': row['id'],
                    'name': row['name'],
                    'encoding': vector
                })
            except Exception as e:
                print(f"[!] Error al cargar encoding de {row['name']}: {e}")
        return known

    def match(self, new_encoding: np.ndarray):
        if not self.known_faces:
            return None  # No hay caras registradas aún

        best_match = None
        min_distance = float('inf')

        for face in self.known_faces:
            distance = np.linalg.norm(new_encoding - face['encoding'])
            if distance < min_distance:
                min_distance = distance
                best_match = face

        if min_distance <= self.threshold:
            return {
                'id': best_match['id'],
                'name': best_match['name'],
                'distance': round(min_distance, 4)
            }
        else:
            return None
