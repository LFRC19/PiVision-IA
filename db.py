# db.py

import sqlite3
import os
from typing import Optional, List, Tuple, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'pivision.db')

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # -------------------------
    # USERS
    # -------------------------
    def add_user(self, username: str, password_hash: str, role: str = 'viewer') -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_users(self) -> List[Tuple]:
        with self._connect() as conn:
            cursor = conn.execute("SELECT id, username, role, created_at FROM users")
            return cursor.fetchall()

    # -------------------------
    # KNOWN FACES
    # -------------------------
    def add_known_face(self, name: str, face_encoding: str, photo_path: Optional[str] = None) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO known_faces (name, face_encoding, photo_path) VALUES (?, ?, ?)",
                (name, face_encoding, photo_path)
            )
            return cursor.lastrowid

    def get_known_faces(self) -> List[Dict]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT id, name, face_encoding, photo_path, is_authorized FROM known_faces"
            )
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # -------------------------
    # DETECTION EVENTS
    # -------------------------
    def log_event(self, camera_id: int, event_type: str, person_id: Optional[int], confidence: float,
                  bounding_box: str, image_path: str):
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO detection_events
                   (camera_id, event_type, person_id, confidence, bounding_box, image_path)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (camera_id, event_type, person_id, confidence, bounding_box, image_path)
            )

    def get_events(self, limit: int = 10) -> List[Dict]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM detection_events ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
