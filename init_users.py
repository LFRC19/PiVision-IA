import sqlite3
from werkzeug.security import generate_password_hash

def init_users_db():
    conn = sqlite3.connect("pivision.db")  
    cursor = conn.cursor()

    # Crear tabla de usuarios si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'viewer'))
    )
    """)

    # Insertar usuario admin por defecto
    try:
        cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """, ("admin", generate_password_hash("admin123"), "admin"))
        print("Usuario administrador creado: admin / admin123")
    except sqlite3.IntegrityError:
        print("El usuario administrador ya existe.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_users_db()
