# init_db.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'pivision.db')

# Esquema SQL con las tres tablas
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'viewer')) NOT NULL DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS known_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    face_encoding TEXT NOT NULL, -- puede ser JSON o base64
    photo_path TEXT,
    is_authorized INTEGER DEFAULT 1, -- BOOLEAN 1=True, 0=False
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS detection_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER,
    event_type TEXT CHECK(event_type IN ('face_detected', 'unknown_person', 'motion', 'gesture')),
    person_id INTEGER,
    confidence REAL,
    bounding_box TEXT, -- JSON string
    image_path TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def init_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(CREATE_TABLES_SQL)
    conn.commit()
    conn.close()

    print(f"[✓] Base de datos inicializada en: {DB_PATH}")

if __name__ == "__main__":
    init_database()
